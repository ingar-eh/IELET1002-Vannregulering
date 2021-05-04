int deviceID = 1; //Hver ESP har sin egen deviceID
int maxWaterLevel = 39; //Max høyde på vann i cm i tanken
int sequence = 5; //Sensoren tar gjennomsnittet av x verdier 
int discardValue = 3; //Hvis to etterfølgende sensor verdier varierer med discardValue (cm) blir de forkastet
//dette er for å fjerne useriøse sensormålinger som kan oppstå
int returnArray[4] = {}; //Et array som skal inneholde deviceID, ventil open / closed, automatisk / manuell og sensorverdi
int sendInterval = 1000; //Intervallet i millisekund vi skal sende data
int triggerPin = 26;
int echoPin = 14;
int greenLed = 12;
int redLed = 27;
int blueLed = 13;
int rightButton = 35;
int leftButton = 34;
int enableMOSFET = 25;
unsigned long prevTime1 = 0; //Brukes i millis()
unsigned long prevTime2 = 0;
int counter = 0;
int pinger = 0;
bool remoteSignal = false;
int sum;
int average; //Gjennomsnittet av sequence antal sensormålinger
int prevAvg;
int valveState; //Leser høyre knapp for å finne ut om man skal åpne / lukke ventiler
bool valveOpen = false;
int readState; //Leser venstre knapp for å finne ut om ESP skal settes i manuell modus
bool manualState;

void setup()
{
  Serial.begin(9600);
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
      sum = sum + (0.01723 * readUltrasonicDistance(triggerPin, echoPin)); //Ganger med 0.01723 for å gjøre om til centimeter
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

bool valveControl(bool manualState, bool remoteSignal) //valveControl leser høyre knapp for å åpne / lukke ventil, eller leser remoteSignal for å åpne / lukke ventil
{
  valveState = analogRead(rightButton);
  if (valveState > 4000){ //Støy i høyre knapp som gir en konstant lav spenning gjennom pin'en,
    //må derfor definere som > 4000 istedet for true
    valveOpen = !valveOpen;
    if (valveOpen == false || manualState == false && remoteSignal == false){
      digitalWrite(redLed, HIGH);
      digitalWrite(greenLed, LOW);
      digitalWrite(enableMOSFET, LOW);     
      }
     else if (valveOpen == true || manualState == false && remoteSignal == false){
      digitalWrite(redLed, LOW);
      digitalWrite(greenLed, HIGH);
      digitalWrite(enableMOSFET, HIGH);
      }
  }
}

int readyArray(int deviceID, bool valveOpen, bool manualState, int average) //Gjør dataen klar for sending ved å konvertere alle verdier til int
{
  return returnArray[0] = deviceID, returnArray[1] = int(valveOpen), 
  returnArray[2] = int(manualState), returnArray[3] = average;
}

void loop()
{
 checkManual();
 
 if (manualState == true && pinger == 1 || manualState == false && remoteSignal == true){
  valveControl(manualState, remoteSignal);
  pinger = 0;
  }
  
  unsigned long currTime2 = millis();
  if (currTime2 - prevTime2 >= sendInterval){
    prevTime2 = currTime2;
    
    returnAverage();
    
    readyArray(deviceID, valveOpen, manualState, average);
    Serial.println(returnArray[3]);
  }
} 
