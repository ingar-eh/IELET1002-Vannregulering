int deviceID = 1; //Hver ESP har sin egen deviceID
int maxWaterLevel = 39; //Max høyde på vann i cm i tanken
int sequence = 5; //Sensoren tar gjennomsnittet av x verdier
int discardValue = 5; //Hvis to etterfølgende sensor verdier varierer med discardValue (cm) blir de forkastet
int counter = 0; // For å forkaste verdier må de først sammenlignes, og for å sammenligne må koden kjøres minst 1 gang
int returnArray[4] = {}; //Et array som skal inneholde deviceID, ventil open / closed, automatisk / manuell og sensorverdi
int triggerPin = 26; //Triggerpin på sensoren
int echoPin = 14; //Echopin på sensoren
int greenLed = 12; //Pin til grønt lys
int redLed = 27; //Pin til rødt lys
int blueLed = 13; //Pin til blått lys
int rightButton = 35; //Pin til høyre knapp, sett fra MOSFET'en
int leftButton = 34; //Pin til venstre knapp
int enableMOSFET = 25; //Pin til MOSFET
float sum; //Summerer opp sequence antal sensormålinger
float average; //Gjennomsnittet av sequence antal sensormålinger
float prevAvg; //Sammenlignes med average for å evt. forkaste verdier
int valveState; //Leser høyre knapp for å finne ut om man skal åpne / lukke ventiler
bool valveOpen; //True betyr ventil er åpen
int readState; //Leser venstre knapp for å finne ut om ESP skal settes i manuell modus
bool manualState; //True betyr ESP er i manuell modus
bool checkState; //Del av bool-logikk for manuell state

bool fetchCommands(){
  if (manualState == false){
    valveOpen = !valveOpen;
    return valveOpen;
  }
}

void setup()
{
  Serial.begin(9600);
  pinMode(redLed, OUTPUT);
  pinMode(greenLed, OUTPUT);
  pinMode(blueLed, OUTPUT);
  pinMode(enableMOSFET, OUTPUT);
  pinMode(rightButton, INPUT);
  pinMode(leftButton, INPUT);
}

bool manual(){
  readState = analogRead(leftButton);
  if (readState > 4000){
    return manualState = !manualState;
  }
  else{
    return manualState;
  }
  }

float readUltrasonicDistance(int triggerPin,int echoPin)
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

bool valveControl(){
  valveState = analogRead(rightButton);
  if (valveState > 4000 && manualState == 1){
    valveOpen = !valveOpen;
  }
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

float returnAverage(){
 prevAvg = average;
 sum = 0;
 for (int i = 0; i < sequence; i++){
    sum = sum + (0.01723 * readUltrasonicDistance(triggerPin, echoPin)); //Ganger med 0.01723 for å gjøre om til centimeter
    delay(75);
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
      else{
        Serial.println("Discarded");
      }
    }
  }
}

void loop()
{
  if (average < 100){
    fetchCommands();
  }
  fetchCommands();
  manual();
  if (manualState == true){
    digitalWrite(blueLed, HIGH);
  }
  else{
    digitalWrite(blueLed, LOW);
  }
  if (checkState == manualState){
    delay(500);
  }
  valveControl();
  returnArray[0] = deviceID; returnArray[1] = valveOpen;
  returnArray[2] = manualState; returnArray[3] = returnAverage();
  checkState = !manualState;
  Serial.println(returnArray[3]);
}
