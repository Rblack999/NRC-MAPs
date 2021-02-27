/* Again from https://www.pythonforthelab.com/blog/how-control-arduino-computer-using-python/
Use this code to 
*/

int analogPin = A0;
int val = 0;
int pump_pin1 = 2;
int pump_pin2 = 4;

void setup() {
  pinMode(LED_BUILTIN,OUTPUT);
  pinMode(pump_pin1,OUTPUT);
  Serial.begin(9600);
  Serial.flush();
}

void loop() {
  if (Serial.available() > 0){                 // When serial command is sent
   int val = char(Serial.read())-'0';          // Conversion of 
    if (val == 1){
      Serial.write("PUMP ON\n");
      digitalWrite(LED_BUILTIN, HIGH);
      digitalWrite(pump_pin1,HIGH);
    }
    if (val == 0){
      Serial.write("PUMP OFF\n");
      digitalWrite(LED_BUILTIN, LOW);
      digitalWrite(pump_pin1,LOW);
    }
  }
}

/* Example python code to control and send start/stop with time
dev = serial.Serial("COM10",baudrate = 9600)
time.sleep(2)
dev.write(b'1')
time.sleep(5)
print(dev.readline().decode('ascii'))
dev.write(b'0')
time.sleep(0.5)
dev.close()
print('closed')

*/
