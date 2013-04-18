#include <IRremote.h>
#include <Wire.h>
#include <Adafruit_MPL115A2.h>


#define PMSHole 2
#define PMSRoom 7
#define PMSKitchen 4
#define MOTIONTIMEOUT 15000

void setup();
void loop();
void IRCheck();
void MotionCheck();
void OnMotionChenged();
IRrecv irrecv(8);
Adafruit_MPL115A2 mpl115a2;
long mpl115a2_lastTime = 0;
decode_results results;


class MotionSens
{
  private:
    long _lastTime; 
    byte _state;
    byte _pin;
    char* _name;
  public:
    MotionSens(char* name, uint8_t pin);
    void check();
};

MotionSens motionRoom("room", PMSRoom);
MotionSens motionHole("hole", PMSHole);
MotionSens motionKitchen("kitchen", PMSKitchen);

void OnMotionChenged();
void IRCheck();

void setup()
{
  Serial.begin(9600);
  irrecv.enableIRIn();
  mpl115a2.begin();
}

void loop()
{
  IRCheck();
  motionHole.check();
  motionRoom.check();
  motionKitchen.check();
  mpl115a2Check();
}

void IRCheck()
{
  if (irrecv.decode(&results))
  {
    Serial.println(results.value, HEX);
    irrecv.resume(); // Receive the next value 
  }
}

MotionSens::MotionSens(char* name, uint8_t pin)
{
      pinMode(pin, INPUT);
      _pin = pin;
      _state = LOW;
      _lastTime = millis();    
      _name = name;  
}

void MotionSens::check()
{
  byte new_state = digitalRead(_pin);
  byte changed = false;
  
  if ((_state == HIGH) && (new_state == LOW) && (millis() - _lastTime > MOTIONTIMEOUT))
  {
      _state = new_state;
      changed = true;
  }
  
  if ((_state == LOW) && (new_state == HIGH))
  {
    _state = new_state;
    changed = true;
    _lastTime = millis();
  }

  if ((_state == HIGH) && (new_state == HIGH))
        _lastTime = millis();
  
  if (changed)
  {
    Serial.print("Motion in ");
    Serial.print(_name);
    if (_state == HIGH)
      Serial.println(" YES");
    else
      Serial.println(" NO");
  }
}

void mpl115a2Check()
{
  if (millis() - mpl115a2_lastTime < 10000)
    return;
  mpl115a2_lastTime = millis();
    
  float pressureKPA = mpl115a2.getPressure();  
  Serial.print("Pressure="); Serial.println(pressureKPA, 4); 

  float temperatureC = mpl115a2.getTemperature();  
  Serial.print("Temp="); Serial.println(temperatureC, 1); 
}


