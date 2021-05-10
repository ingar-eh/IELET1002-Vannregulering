//Importerer bibilotek for SPI-kommunikasjon, samt RF-modulens bibliotek
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

//Definerer CE og CSN-pinnene som RF-modulen bruker
#define CE 17
#define CSN 5

//Kommunikasjonsadressen
//Merk at begge enhetene deler samme adresse
const byte thisSlaveAddress[5] = {'E', 'S', 'P', '0', '3'};

//Starter en RF24-objekt
RF24 radio(CE, CSN);

byte piControl = 1;       //Dataen som blir mottatt
int returnArray[3];      //ACK-payload
bool newData = false;    //Sjekker om ny data skal mottas

const int maxWaterLevel = 390; //Max høyde på vann i cm i tanken
const int sequence = 5; //Sensoren tar gjennomsnittet av x verdier 
const int discardValue = 3; //Hvis to etterfølgende sensor verdier varierer med discardValue (cm) blir de forkastet
//dette er for å fjerne useriøse sensormålinger som kan oppstå
const int sendInterval = 5000; //Intervallet i millisekund vi skal sende data
const int triggerPin = 14;
const int echoPin = 26;
const int greenLed = 12;
const int redLed = 27;
const int blueLed = 13;
const int rightButton = 35;
const int leftButton = 34;
const int enableMOSFET = 25;
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

//Deklarering av funksjoner
void getData(void);
void showData(void);
void updateReplyData(void);

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
//========

/*
 * Funksjon som tar 1 sensormåling
 * Argumenter - triggerPin, echoPin
 * Gir tilbake - pulseIn(echoPin, HIGH);
 * 
 */
float readUltrasonicDistance(int triggerPin, int echoPin)
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
//========

/*
 * Funksjon som klargjør returnerer gjennomsnittet av sequence antal sensorverdier, og evt. forkaster tullete verdier
 * Argumenter - ingen
 * Gir tilbake - average
 * 
 * Variabler brukt i funksjonen:
 * prevAvg ---> sammenlignende verdi
 * average --> tidligere og nåverende sensorverdi
 * sequence --> hvor mange målinger vi vil ta gjennomsnittet av
 * sum --> summeres opp for å kunne ta gjennomsnitt
 * discardValue --> max forskjell mellom to etterfølgende sensorverdier
 * counter --> brukes for at koden ikke skal prøve å sammenligne når den kjøres for første gang
 */
int returnAverage()
{ 
 prevAvg = average;
 sum = 0;
 for (int i = 0; i < sequence; i++){
      sum = sum + (0.01723 * readUltrasonicDistance(triggerPin, echoPin)); //Ganger med 0.1723 for å gjøre om til millimeter
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
//========

/*
 * Funksjon som leser knapp og endrer manuellkontroll ettersom
 * Argumenter - ingen
 * Gir tilbake - manualState, pinger
 * 
 * Variabler brukt i funksjonen:
 * prevTime1 ---> brukes i millis()
 * readState --> leser venstre knapp
 * manualState --> manuellkontroll eller ikke
 */
bool checkManual()
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
//========

/*
 * Funksjon som styrer ventilene
 * Argumenter - manuellkontroll, Pi-kontroll
 * Gir tilbake - ingenting
 * 
 * Variabler brukt i funksjonen:
 * valveState --> om knapp blir trykt inn
 * valveOpen --> om valve skal åpnes
 * manualState --> om den er i manuellkontroll
 * piControl --> om den mottar signal fra Pi'en
 */
bool valveControl(bool manualState, byte piControl)
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
//========

/*
 * Funksjon som klargjør data for sending til Pi'en
 * Argumenter - ventil-tilstand, manuellkontroll, sensorverdier
 * Gir tilbake - returnArray
 * 
 * Variabler brukt i funksjonen:
 * readyArray ---> Data som står i ACK-payload
 */
int readyArray(bool valveOpen, bool manualState, int average)
{
  return returnArray[0] = int(valveOpen), 
  returnArray[1] = int(manualState), returnArray[2] = average;
}
//========

/*
 * Funksjon som får data fra transmitter-enheten
 * Argumenter - ingen
 * Gir tilbake - ingenting
 * 
 * Variabler brukt i funksjonen:
 * piControl ---> Datastreng mottatt fra RF-kommunikasjon
 * newData ---> Viser om vi har ny data som skal skrives ut
 */
void getData()
{
  //Hvis det er bytes i bufferen til radio-enheten (hvis informasjon skal leses)
  if(radio.available()){
    radio.read(&piControl, sizeof(piControl));      //les informasjonen
    updateReplyData();                              //Oppdater svar data (sjekk funksjonen nedenfor)
    newData = true;                                 //Data har blitt mottatt
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
 * piControl ---> Datastreng mottatt fra RF-kommunikasjon
 * returnArray ---> Data som står i ACK-payload
 */
void showData()
{
  if(newData == true){
    Serial.print("Data received ");
    Serial.println(piControl);
    Serial.print("ACK payload sent: ");
    Serial.print(returnArray[0]);
    Serial.print(", ");
    Serial.print(returnArray[1]);
    Serial.print(", ");
    Serial.println(returnArray[2]);
    newData = false;
  }
}

//========

/*
 * Funksjon som oppdaterer svardata
 * Argumenter - ingen
 * Gir tilbake - ingenting
 * 
 * Variabler brukt i funksjonen:
 * valveOpen ---> ventiltilstand
 * manualState --> manuellkontroll
 * average --> sensorverdier
 * returnArray --> data som skal sendes
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
  }
  getData();                                                
  showData();
} 
