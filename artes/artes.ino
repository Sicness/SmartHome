#include <OneWire.h>
#include <Wire.h>
#include <IRremote.h>
#include <SPI.h>
#include <Adafruit_MPL115A2.h>

#define PMSHole 2
#define MOTIONTIMEOUT 15000
//#define LED1 7
#define SND 9

#define SensorMotionOff 0
#define SensorMotionOn  1
#define SensorMotionDetect 2

OneWire ds(3);
Adafruit_MPL115A2 mpl115a2;

/*byte ds_addr[8];
byte ds_data[12];
byte ds_present = 0;
long ds_lastTime = 0;
*/
long mpl115a2_lastTime = 99999;  // for run immediately

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
void dsCheck();
void mpl115a2Check();

void setup()
{
  HoleMotion.pin = PMSHole;
  HoleMotion.state = LOW;
  HoleMotion.mode = SensorMotionDetect;
  HoleMotion.lastTime = millis();
  
  //pinMode(LED1, OUTPUT);
  pinMode(SND, OUTPUT);
  
  Serial.begin(9600);
  irrecv.enableIRIn();
  
  mpl115a2.begin();
  /*
  // Init DS1820 temperature sernosor
  if (! ds.search(ds_addr))
  {
    Serial.println("no more addr");
    ds.reset_search();
    return;
  }

  if ( OneWire::crc8( ds_addr, 7) != ds_addr[7]) {
      Serial.print("CRC is not valid!\n");
      return;
  }

  if ( ds_addr[0] == 0x10) 
  {
      Serial.print("Device is a DS18S20 family device.\n");
  }
  
  else {
      Serial.print("Device family is not recognized: 0x");
      Serial.println(ds_addr[0],HEX);
      return;
  }
  
  
  ds_present = ds.reset();
  ds.select(ds_addr);    
  ds.write(0x44);         // Read Scratchpad
  ds_lastTime = millis();
  */
}

void loop()
{
  IRCheck();
  MotionCheck();
  //dsCheck(); replaced by mpl115a2
}

void IRCheck()
{
  if (irrecv.decode(&results))
  {
    switch (results.value)
    {
      //case 0xFFE01F: HoleMotion.mode = SensorMotionOff; 
        //Serial.println("HMSoff"); break;
      default: Serial.println(results.value);
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
    { HoleMotion.state = LOW; /*digitalWrite(LED1, LOW);*/ return; }
  if ( HoleMotion.mode == SensorMotionOn)
    { HoleMotion.state = HIGH; /*digitalWrite(LED1, HIGH);*/ return; }
  
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

  if ( (HoleMotion.state == HIGH) && (state == HIGH) )
        HoleMotion.lastTime = millis();
  
  // Triger
  if(changedState)
    OnMotionChenged();
}

void OnMotionChenged()
{
  Serial.print("hole ");
  if ( HoleMotion.state == HIGH )
    {
      Serial.println("ON");
      //digitalWrite(LED1, HIGH);
    }
  else
  {
    Serial.println("OFF");
    //digitalWrite(LED1, LOW);
  }
}
/*
void dsCheck()
{
  //Serial.println("");
 // Serial.print(millis());
  //Serial.print(" ");
  //Serial.println(ds_lastTime);
  if (millis() - ds_lastTime < 10000)
    return;
    
  int LowByte, HighByte, TReading, SignBit,Tc_100,Whole, Fract;
  char buf[6];
  ds_present = ds.reset();
  ds.select(ds_addr);    
  ds.write(0xBE);         // Read Scratchpad

  for ( int i = 0; i < 9; i++) 
  {           // we need 9 bytes
    ds_data[i] = ds.read();
  }

  LowByte = ds_data[0];
  HighByte = ds_data[1];
  TReading = (HighByte << 8) + LowByte;
  SignBit = TReading & 0x8000;  // test most sig bit
  if (SignBit) // negative
  {
    TReading = (TReading ^ 0xffff) + 1; // 2's comp
  }
  Tc_100 = (TReading*100/2);    

  Whole = Tc_100 / 100;  // separate off the whole and fractional portions
  Fract = Tc_100 % 100;

  sprintf(buf, "T=%d.%d\0", Whole, (Fract < 10 ? 0 : Fract) / 10);
  Serial.println(buf);
    
  ds.reset();
  ds.select(ds_addr);
  ds.write(0x44,1);         // new calculation
  ds_lastTime = millis();
}
*/

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
