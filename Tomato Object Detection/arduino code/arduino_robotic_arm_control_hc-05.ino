//Stepper Pins
const int stepPin = 3, dirPin = 4;
int led = 13;  //---------------------------
//Bluetooth Communications Variables
float x, y;
int x_rvd, y_rvd;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);

  pinMode(led, OUTPUT);  //---------------------
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available()) {
    digitalWrite(led, HIGH);
    delay(500);
    digitalWrite(led, LOW);

    bluetooth_comm();
    stepper();
  }
}

void bluetooth_comm() {
  x_rvd = Serial.parseInt();
  x = (float) x_rvd/100;
  Serial.print("x: ");
  Serial.println(x);

  y_rvd = Serial.parseInt();
  y = (float) y_rvd/100;
  Serial.print("y: ");
  Serial.println(y);
}

void stepper() {
  if (x < 0) {
    digitalWrite(dirPin, HIGH);
  Serial.println("Anti-Clockwise");
  } else {
    digitalWrite(dirPin, LOW);
  Serial.println("Clockwise");
  }
  const float mov_in_1_step = 0.05;     // 0.0785
  int x_rvdput = abs(round(x / mov_in_1_step));
  Serial.println(x_rvdput);

  for (int i = 0; i < x_rvdput; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(500);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(500);
  }
}
