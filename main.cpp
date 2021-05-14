//Importerer bibilotek for SPI-kommunikasjon, samt RF-modulens bibliotek
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <esp32_pindefs.h>

//Kommunikasjonsadressen
//Merk at begge enhetene deler samme adresse
const byte thisSlaveAddress[5] = {'E', 'S', 'P', '0', '2'};

//Starter en RF24-objekt
RF24 radio(CE, CSN);

byte piControl;       //Dataen som blir mottatt
byte remote;
int returnArray[3];      //ACK-payload
bool newData = false;    //Sjekker om ny data skal mottas

unsigned long prevTime1 = 0; //Brukes i millis()
unsigned long prevTime2 = 0;
int counter = 0;
byte bounceBck = 0;
int sum;
int average; //Gjennomsnittet av sequence antal sensormålinger
int prevAvg;
int valveState; //Leser høyre knapp for å finne ut om man skal åpne / lukke ventiler
bool valveOpen = false;
int readState; //Leser venstre knapp for å finne ut om ESP skal settes i manuell modus
bool manualState;

//Deklarering av funksjoner
byte getData(void);
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
float readUltrasonicDistance()
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
      sum = sum + (0.01723 * readUltrasonicDistance()); //Ganger med 0.1723 for å gjøre om til millimeter
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
          return manualState, bounceBck = 1;
          break;
        case false:
          digitalWrite(blueLed, LOW);
          return manualState, bounceBck = 1;
      }
    }
    else{
      return manualState, bounceBck = 1; 
    }
   }
 }
//========

/*
 * Funksjon som styrer ventilene
 * Argumenter - manuellkontroll, Pi-kontroll
 * Gir tilbake - valveOpen
 * 
 * Variabler brukt i funksjonen:
 * valveState --> om knapp blir trykt inn
 * valveOpen --> om valve skal åpnes
 * manualState --> om den er i manuellkontroll
 * piControl --> om den mottar signal fra Pi'en
 */
bool valveControl(bool manualState, byte piControl, byte remote)
{
  valveState = analogRead(rightButton);
  if (valveState > 4000 && manualState == 1){ //Støy i høyre knapp som gir en konstant lav spenning gjennom pin'en,
    //må derfor definere som > 4000 istedet for true
    valveOpen = !valveOpen;
    if (valveOpen == false){
      digitalWrite(redLed, HIGH);
      digitalWrite(greenLed, LOW);
      digitalWrite(enableMOSFET, LOW);     
      } 
     else if (valveOpen == true){
      digitalWrite(redLed, LOW);
      digitalWrite(greenLed, HIGH);
      digitalWrite(enableMOSFET, HIGH);
      }
  }
  else if (manualState == false && remote == 1){
    if (piControl == 0){
      digitalWrite(redLed, HIGH);
      digitalWrite(greenLed, LOW);
      digitalWrite(enableMOSFET, LOW);
      return valveOpen = false;
    }
    else{
      digitalWrite(redLed, LOW);
      digitalWrite(greenLed, HIGH);
      digitalWrite(enableMOSFET, HIGH);
      return valveOpen = true;
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
byte getData()
{
  //Hvis det er bytes i bufferen til radio-enheten (hvis informasjon skal leses)
  if(radio.available()){
    radio.read(&piControl, sizeof(piControl));      //les informasjonen
    updateReplyData();                              //Oppdater svar data (sjekk funksjonen nedenfor)
    newData = true;
    return piControl;//Data har blitt mottatt
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
 if (manualState == true && bounceBck == 1){
  valveControl(manualState, piControl, 0);
  bounceBck = 0;
  }
 else if(manualState == false){
  valveControl(manualState, piControl, 1);
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
