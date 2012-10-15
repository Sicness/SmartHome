#include <IRremote.h>

#define PMSHole 2
#define MOTIONTIMEOUT 5000
#define LED1 7

#define SensorMotionOff 0
#define SensorMotionOn  1
#define SensorMotionDetect 2

IRrecv irrecv(8);
decode_results results;

struct TmotionSens
{
  byte pin;
  byte state;
  byte mode;
  long lastTime;
} HoleMotion;

void MotionCheck();
void OnMotionChenged();
void IRCheck();

void setup()
{
  HoleMotion.pin = PMSHole;
  HoleMotion.state = LOW;
  HoleMotion.mode = SensorMotionDetect;
  HoleMotion.lastTime = millis();
  
  pinMode(LED1, OUTPUT);
  
  Serial.begin(9600);
  irrecv.enableIRIn();
}

void loop()
{
  IRCheck();
  MotionCheck();
  delay(100);
 
  //tone(8,700,50); 
}

void IRCheck()
{
  if (irrecv.decode(&results))
  {
    Serial.println(results.value, HEX);
    switch (results.value)
    {
      case 0xFFE01F: HoleMotion.mode = SensorMotionOff; 
        Serial.println("HMSoff"); break;
      case 0xFFA857: HoleMotion.mode = SensorMotionOn;
        Serial.println("HMSon"); break;
      case 0xFF906F: HoleMotion.mode = SensorMotionDetect; 
        Serial.println("HMSdetect");break;
      //FFA25D
//FFE21D
      case 0xFFA25D: Serial.println("VoiceOff"); break;
      case 0xFFE21D: Serial.println("VoiceOn"); break;

    }
    irrecv.resume(); // Receive the next value
  }
}

void MotionCheck()
{
  byte state = digitalRead(HoleMotion.pin);
  //Serial.println(state);
  bool changedState = false;
  
  if ( HoleMotion.mode == SensorMotionOff)
    { HoleMotion.state = LOW; digitalWrite(LED1, LOW); return; }
  if ( HoleMotion.mode == SensorMotionOn)
    { HoleMotion.state = HIGH; digitalWrite(LED1, HIGH); return; }
  
  if ( (HoleMotion.state == HIGH) && (state == LOW) && ( millis() - HoleMotion.lastTime > MOTIONTIMEOUT))
  // Switch off sensor and save info
  {
    HoleMotion.state = state;
    changedState = true;
  }
  
  if ( (HoleMotion.state == LOW) && (state == HIGH) )
  {
    HoleMotion.state = state;
    HoleMotion.lastTime = millis();
    changedState = true;
   }
  
  // Triger
  if(changedState)
    OnMotionChenged();
}

void OnMotionChenged()
{
  Serial.print("hole motion");
  if ( HoleMotion.state == HIGH )
    {
      Serial.println(" ON");
      digitalWrite(LED1, HIGH);
    }
  else
  {
    Serial.println("OFF");
    digitalWrite(LED1, LOW);
  }
}
