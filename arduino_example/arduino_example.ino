unsigned long zero_time;
unsigned long curr_time;
int message_rate=1000;
int pinstat=0;
// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:

  pinMode(13,OUTPUT);
  Serial.begin(115200);
  zero_time=millis();
  
}

// the loop routine runs over and over again forever:
void loop() {
 
  if (Serial.available()>0){
    // wait for the whole message
    String message=String("          ");
    int i=0;
    while(Serial.available()>0){
      message[i]=Serial.read();
      i++;
      }
    message_rate=message.toInt();
    pinstat++;
    digitalWrite(13,pinstat%2);  
    }
  
  curr_time=millis();
  int sensorValue = analogRead(A0);
  // print time
  Serial.print(curr_time-zero_time);
  // delimiter between time and value
  Serial.print("/");
  // print sensor's value
  Serial.println(sensorValue);
  delay(message_rate);        // delay in between reads for stability
}
