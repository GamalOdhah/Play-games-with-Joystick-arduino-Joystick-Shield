void setup() {
  Serial.begin(9600);
  pinMode(2, INPUT_PULLUP);
  pinMode(3, INPUT_PULLUP);
  pinMode(4, INPUT_PULLUP);
  pinMode(5, INPUT_PULLUP);  
  pinMode(6, INPUT_PULLUP); 
}

void loop() {
  int x = analogRead(A0);
  int y = analogRead(A1);
  int joyBtn = digitalRead(2);
  int btnA = digitalRead(3);
  int btnB = digitalRead(4);
  int btnC = digitalRead(5);
  int btnD = digitalRead(6);
  
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.print(",");
  Serial.print(joyBtn);
  Serial.print(",");
  Serial.print(btnA);
  Serial.print(",");
  Serial.print(btnB);
  Serial.print(",");
  Serial.print(btnC);
  Serial.print(",");
  Serial.println(btnD);
  
  delay(100);  
}