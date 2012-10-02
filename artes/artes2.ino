#define PMSHole 3
#define MOTIONTIMEOUT 5000

struct TmotionSens
{
  byte pin;
  byte state;
  long lastTime;
} HoleMotion;

void MotionCheck();
void OnMotionChenged();

void setup()
{
  HoleMotion.pin = PMSHole;
  HoleMotion.state = LOW;
  HoleMotion.lastTime = millis();
}

void loop()
{
  MotionCheck();
  
  Serial.begin(9600);
}

void MotionCheck()
{
  byte state = digitalRead(HoleMotion.pin);
  bool changedState = false;
  
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
  OnMotionChenged();
}

void OnMotionChenged()
{
  Serial.print("hole motion");
  if ( HoleMotion.state == HIGH )
    Serial.println("on");
  else
    Serial.println("off");
}
