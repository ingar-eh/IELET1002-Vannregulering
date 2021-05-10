//Importerer bibilotek for SPI-kommunikasjon, samt RF-modulens bibliotek
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

//Definerer CE og CSN-pinnene som RF-modulen bruker
#define CE 17
#define CSN 5

//Kommunikasjonsadressen
//Merk at begge enhetene deler samme adresse
const byte thisSlaveAddress[] = {'E', 'S', 'P', '0', '1'};

//Starter en RF24-objekt
RF24 radio(CE, CSN);

byte piControl;                                             //Dataen som blir mottatt
int returnArray[3];      //ACK-payload
bool newData = false;                                              //Sjekker om ny data skal mottas

//Deklarering av funksjoner
void getData(void);
void showData(void);
void updateReplyData(void);

#define maxWaterLevel = 390; //Max høyde på vann i cm i tanken
#define sequence = 5; //Sensoren tar gjennomsnittet av x verdier 
#define discardValue = 3; //Hvis to etterfølgende sensor verdier varierer med discardValue (cm) blir de forkastet
//dette er for å fjerne useriøse sensormålinger som kan oppstå
#define sendInterval = 1000; //Intervallet i millisekund vi skal sende data
#define triggerPin = 26;
#define echoPin = 14;
#define greenLed = 12;
#define redLed = 27;
#define blueLed = 13;
#define rightButton = 35;
#define leftButton = 34;
#define enableMOSFET = 25;
unsigned long prevTime1 = 0; //Brukes i millis()
unsigned long prevTime2 = 0;
int counter = 0;
byte pinger = 0;
int sum;
int average; //Gjennomsnittet av sequence antal sensormålinger
int prevAvg;
int valveState; //Leser høyre knapp for å finne ut om man skal åpne / lukke ventiler
bool valveOpen = false;
int readState; //Leser venstre knapp for å finne ut om ESP skal settes i manuell modus
bool manualState;

void setup()
{
  Serial.begin(115200);
  
  Serial.println("Receiver with ACK payload starting: ");
  radio.begin();                                            //Starter RF-modulen
  radio.setDataRate(RF24_250KBPS);                          //Oppsett av data rate
  radio.openReadingPipe(1, thisSlaveAddress);               //Åpner en lesingkanal

  radio.enableAckPayload();                                 //Aktiverer ACK-signalet
  radio.startListening();                                   //Starter receiver-modus

  radio.writeAckPayload(1, &returnArray, sizeof(returnArray));      //Skriver ACK-payload i minnet
  pinMode(redLed, OUTPUT);
  pinMode(greenLed, OUTPUT);
  pinMode(blueLed, OUTPUT);
  pinMode(enableMOSFET, OUTPUT);
  pinMode(rightButton, INPUT);
  pinMode(leftButton, INPUT);
  digitalWrite(redLed, HIGH);
}

float readUltrasonicDistance(int triggerPin, int echoPin) //readUltrasonicDistance leser 1 sensormåling
{
  pinMode(triggerPin, OUTPUT);
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);
  pinMode(echoPin, INPUT);
  return pulseIn(echoPin, HIGH);
}

int returnAverage()//Tar sequence antall sensormålinger og returnerer gjennomsnittet, filtrerer også ut useriøse verdier
{ 
 prevAvg = average;
 sum = 0;
 for (int i = 0; i < sequence; i++){
      sum = sum + (0.1723 * readUltrasonicDistance(triggerPin, echoPin)); //Ganger med 0.1723 for å gjøre om til millimeter
      delay(50); //Må sette en liten brems på hver sensormåling, ellers klikker sensoren
      if (i == (sequence - 1)){
        average = sum / sequence;
        //average = maxWaterLevel - average; //Sensor måler 1 cm fra toppen, sensorverdi minus total verdi gir vannnivå fra bunn til topp.
        if (counter == 1 && abs(average - prevAvg) < discardValue){
          return average;
        }
        else if (counter == 0){
          counter = 1;
          return average;
        }
      }
    }
} 

bool checkManual()//checkManual() leser venstre knapp for å finne ut om programmet skal inn / ut av manuell modus,
{
  unsigned long currTime1 = millis(); //Lager et intervall slik at en knappe-endring bare kan skje med minst 1 sekunds mellomrom,
  //det er for at LED'ene ikke skal hoppe frem og tilbake 100 ganger mens knappen blir holdt nede.
  if (currTime1 - prevTime1 >= 1000){
    prevTime1 = currTime1;
    readState = analogRead(leftButton);
    if (readState > 4000){
      manualState = !manualState;
      switch(manualState){
        case true:
          digitalWrite(blueLed, HIGH);
          return manualState, pinger = 1;
          break;
        case false:
          digitalWrite(blueLed, LOW);
          return manualState, pinger = 1;
      }
    }
    else{
      return manualState, pinger = 1; 
    }
   }
 }

bool valveControl(bool manualState, byte piControl) //valveControl leser høyre knapp for å åpne / lukke ventil, eller leser remoteSignal for å åpne / lukke ventil
{
  valveState = analogRead(rightButton);
  if (valveState > 4000){ //Støy i høyre knapp som gir en konstant lav spenning gjennom pin'en,
    //må derfor definere som > 4000 istedet for true
    valveOpen = !valveOpen;
    if (valveOpen == false || manualState == false && piControl == false){
      digitalWrite(redLed, HIGH);
      digitalWrite(greenLed, LOW);
      digitalWrite(enableMOSFET, LOW);     
      }
     else if (valveOpen == true || manualState == false && piControl == false){
      digitalWrite(redLed, LOW);
      digitalWrite(greenLed, HIGH);
      digitalWrite(enableMOSFET, HIGH);
      }
  }
}

int readyArray(bool valveOpen, bool manualState, int average) //Gjør dataen klar for sending ved å konvertere alle verdier til int
{
  return returnArray[0] = int(valveOpen), 
  returnArray[1] = int(manualState), returnArray[2] = average;
}

/*
 * Funksjon som får data fra transmitter-enheten
 * Argumenter - ingen
 * Gir tilbake - ingenting
 * 
 * Variabler brukt i funksjonen:
 * dataReceived ---> Datastreng mottatt fra RF-kommunikasjon
 * newData ---> Viser om vi har ny data som skal skrives ut
 */
void getData()
{
  //Hvis det er bytes i bufferen til radio-enheten (hvis informasjon skal leses)
  if(radio.available()){
    radio.read(&piControl, sizeof(piControl));            //les informasjonen
    updateReplyData();                                          //Oppdater svar data (sjekk funksjonen nedenfor)
    newData = true;                                             //Data har blitt mottatt
  }
}

//========

/*
 * Funksjon som skriver ut mottatt data og ACK-payload som blir sendt tilbake
 * Argumenter - ingen
 * Gir tilbake - ingenting
 * 
 * Variabler brukt i funksjonen:
 * newData ---> Viser om vi har ny data som skal skrives ut
 * dataReceived ---> Datastreng mottatt fra RF-kommunikasjon
 * ackData ---> Data som står i ACK-payload
 */
void showData()
{
  //Hvis vi har mottatt data, skriver vi ut dataen og ACK-payload som er sendt tilbake
  if(newData == true){
    Serial.print("Data received ");
    Serial.println(piControl);
    Serial.print("ACK payload sent: ");
    Serial.print(returnArray[0]);
    Serial.print(", ");
    Serial.print(returnArray[1]);
    Serial.print(", ");
    Serial.println(returnArray[2]);
    newData = false;                      //Reset newData slik at vi får ny data i neste innsending
  }
}

//========

/*
 * Funksjon som oppdaterer svardata
 * Argumenter - ingen
 * Gir tilbake - ingenting
 * 
 * Variabler brukt i funksjonen:
 * readyArray ---> Data som står i ACK-payload
 */
void updateReplyData()
{
  readyArray(valveOpen, manualState, average);
  radio.writeAckPayload(1, &returnArray, sizeof(returnArray));
}

void loop()
{
 checkManual();
 
 if (manualState == true && pinger == 1 || manualState == false && piControl == true){
  valveControl(manualState, piControl);
  pinger = 0;
  }
  
  unsigned long currTime2 = millis();
  if (currTime2 - prevTime2 >= sendInterval){
    prevTime2 = currTime2;
    
    returnAverage();
       
    readyArray(valveOpen, manualState, average);
    //Serial.println(returnArray[3]);
    
    getData();                                                
    showData();
  }
} 
