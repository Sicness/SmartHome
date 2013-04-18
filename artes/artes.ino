#include <IRremote.h>
#include <Wire.h>
#include <Adafruit_MPL115A2.h>


#define PMSHole 2
#define PMSRoom 7
#define MOTIONTIMEOUT 15000

void setup();
void loop();
void IRCheck();
void MotionCheck();
void OnMotionChenged();
IRrecv irrecv(8);
Adafruit_MPL115A2 mpl115a2;
long mpl115a2_lastTime = 0;
byte motionSensHoleLast, motionSensRoomLast;
decode_results results;


class MotionSens
{
  private:
    long _lastTime; 
    byte _state;
    byte _pin;
  public:
    MotionSens(uint8_t pin)
    {
      pinMode(pin, INPUT);
      _pin = pin;
      _state = LOW;
      _lastTime = millis();      
    }
    byte check();
};

byte MotionSens::check()
{
  byte new_state = digitalRead(_pin);
  Serial.print("read: ");
  Serial.write(new_state + 0x30);
  Serial.println("");
  
  if ((_state == HIGH) && (new_state == LOW) && (millis() - _lastTime > MOTIONTIMEOUT))
    _state = new_state;
  
  if ((_state == LOW) && (new_state == HIGH))
  {
    _state = new_state;
    _lastTime = millis();
  }

  if ((_state == HIGH) && (new_state == HIGH))
        _lastTime = millis();
  
  return _state;
}

MotionSens motionRoom(PMSRoom);
MotionSens motionHole(PMSHole);
//MotionSens kitchen;

void MotionCheck()
{
  byte newstate;
 
  newstate = motionHole.check();
  Serial.print("MoH: "); Serial.write(motionSensHoleLast + 0x30);
  Serial.write(newstate + 0x30); Serial.println("");
  
  if (newstate != motionSensHoleLast)
  {
    Serial.print("Motion in hole ");
    if (newstate == HIGH)
      Serial.println("YES");
    else
      Serial.println("NO");
    motionSensHoleLast = newstate;
  }
  
  newstate = motionRoom.check();
    Serial.print("MoR: "); Serial.write(motionSensRoomLast+0x30);
  Serial.write(newstate+0x30); Serial.println("");
  if (newstate != motionSensRoomLast)
  {
    Serial.print("Motion in room ");
    if (newstate == HIGH)
      Serial.println("YES");
    else
      Serial.println("NO");
    motionSensRoomLast = newstate;
  }
  delay(1000);
}

void OnMotionChenged();
void IRCheck();

void setup()
{
  motionSensHoleLast = motionHole.check();
  motionSensRoomLast = motionRoom.check();
  
  Serial.begin(9600);
  irrecv.enableIRIn();
  mpl115a2.begin();
}

void loop()
{
  IRCheck();
  MotionCheck();
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


