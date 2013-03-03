#include <IRremote.h>
#include <Adafruit_MPL115A2.h>


#define PMSHole 2
#define MOTIONTIMEOUT 15000

#define SensorMotionOff 0
#define SensorMotionOn  1
#define SensorMotionDetect 2

void setup();
void loop();
void IRCheck();
void MotionCheck();
void OnMotionChenged();
IRrecv irrecv(8);
Adafruit_MPL115A2 mpl115a2;
long mpl115a2_lastTime = 0;
decode_results results;

struct MotionSens
{
  byte pin;
  byte state;
  byte mode;
  long lastTime;
} holeMotion;

void MotionCheck();
void OnMotionChenged();
void IRCheck();

void setup()
{
  holeMotion.pin = PMSHole;
  holeMotion.state = LOW;
  holeMotion.mode = SensorMotionDetect;
  holeMotion.lastTime = millis();
  
  Serial.begin(9600);
  irrecv.enableIRIn();
  mpl115a2.begin();
}

void loop()
{
  IRCheck();
  MotionCheck();
}

void IRCheck()
{
  if (irrecv.decode(&results))
  {
    Serial.println(results.value, HEX);
    irrecv.resume(); // Receive the next value 
  }
}

void MotionCheck()
{
  byte new_state = digitalRead(holeMotion.pin);
  bool changedState = false;
  
  if ( (holeMotion.state == HIGH) && (new_state == LOW) && ( millis() - holeMotion.lastTime > MOTIONTIMEOUT))
  {
    holeMotion.state = new_state;
    changedState = true;
  }
  
  if ( (holeMotion.state == LOW) && (new_state == HIGH) )
  {
    holeMotion.state = new_state;
    holeMotion.lastTime = millis();
    changedState = true;
   }

  if ( (holeMotion.state == HIGH) && (new_state == HIGH) )
        holeMotion.lastTime = millis();
  
  // Triger
  if(changedState)
    OnMotionChenged();
}

void OnMotionChenged()
{
  Serial.print("hole ");
  if ( holeMotion.state == HIGH )
    Serial.println("ON");
  else
    Serial.println("OFF");
}

void mpl115a2Check()
{
  if (millis() - mpl115a2_lastTime < 10000)
    return;
  mpl115a2_lastTime = millis();
    
  float pressureKPA = mpl115a2.getPressure();  
  Serial.print("Pressure="); Serial.print(pressureKPA, 4); Serial.println(" kPa");

  float temperatureC = mpl115a2.getTemperature();  
  Serial.print("Temp="); Serial.print(temperatureC, 1); Serial.println(" *C");
}


