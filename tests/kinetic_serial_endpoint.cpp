// KINETIC Serial Endpoint Code Generation
// Auto-Generated

// See documentation on pinouts and additional information.

int incomingData;
int accumulatorIndex = 0;
char accumulator[64];

bool motorIsReadingSpeedMotorLeft = false;
bool motorIsReadingSpeedMotorRight = false;
void setup() {
    Serial.begin(9600);

    pinMode(3, OUTPUT); // PWM CONTROL FOR MotorLeft
    pinMode(2, OUTPUT); // DIRECTION CONTROL FOR MotorLeft
    pinMode(4, OUTPUT); // BRAKE CONTROL FOR MotorLeft
    pinMode(9, OUTPUT); // PWM CONTROL FOR MotorRight
    pinMode(5, OUTPUT); // DIRECTION CONTROL FOR MotorRight
    pinMode(6, OUTPUT); // BRAKE CONTROL FOR MotorRight
}

void loop() {

    if (Serial.available() > 0) {

        incomingData = Serial.read();

        if (incomingData == 0x0A) { // 0x0A is the decimal code for a newline character, when it's received, the accumulator is dumped and evaluated
            accumulatorIndex = 0; // reset accumulator write index
            if (strcmp(accumulator, "MOTOR_BRAKE_HOLD MotorLeft") == 0) {
                digitalWrite(4, HIGH);
            }
            if (strcmp(accumulator, "MOTOR_BRAKE_RELEASE MotorLeft") == 0) {
                digitalWrite(4, LOW);
            }
            if (strcmp(accumulator, "MOTOR_FORWARD MotorLeft") == 0) {
                digitalWrite(2, HIGH);
            }
            if (strcmp(accumulator, "MOTOR_BACKWARD MotorLeft") == 0) {
                digitalWrite(2, LOW);
            }
            if (strcmp(accumulator, "MOTOR_SPEED MotorLeft") == 0) {
                motorIsReadingSpeedMotorLeft = true;
            }
            if (motorIsReadingSpeedMotorLeft == true) {
                analogWrite(3, atoi(accumulator));
                motorIsReadingSpeedMotorLeft = false;
            }
            if (strcmp(accumulator, "MOTOR_BRAKE_HOLD MotorRight") == 0) {
                digitalWrite(6, HIGH);
            }
            if (strcmp(accumulator, "MOTOR_BRAKE_RELEASE MotorRight") == 0) {
                digitalWrite(6, LOW);
            }
            if (strcmp(accumulator, "MOTOR_FORWARD MotorRight") == 0) {
                digitalWrite(5, HIGH);
            }
            if (strcmp(accumulator, "MOTOR_BACKWARD MotorRight") == 0) {
                digitalWrite(5, LOW);
            }
            if (strcmp(accumulator, "MOTOR_SPEED MotorRight") == 0) {
                motorIsReadingSpeedMotorRight = true;
            }
            if (motorIsReadingSpeedMotorRight == true) {
                analogWrite(9, atoi(accumulator));
                motorIsReadingSpeedMotorRight = false;
            }

            memset(accumulator, 0, sizeof(accumulator)); // clears array.
        }
        else {
            if (accumulatorIndex <= 63) {
                accumulator[accumulatorIndex] = incomingData;
                accumulatorIndex += 1;
            }
        }
    }
}
    