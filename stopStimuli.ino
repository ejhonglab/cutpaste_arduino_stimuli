
// TODO put these variables into header file, shared w/ stimulus code
const int scopePin = 46;
const int olfDispPin = 47; 
const int flowPin = 48;
const int mirrorPin = 49;

//int activeOlfPins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11};
int activeOlfPins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 31, 26, 27, 50, 51};
int numPins=sizeof(activeOlfPins)/sizeof(int); 

 
void setup() {
  pinMode(scopePin, OUTPUT);
  pinMode(olfDispPin, OUTPUT);
  pinMode(flowPin, OUTPUT);
  pinMode(mirrorPin, OUTPUT);

  digitalWrite(olfDispPin, LOW);
  digitalWrite(flowPin, LOW);
  digitalWrite(mirrorPin, LOW);

  for (int i=0; i < numPins; i++){
    pinMode(activeOlfPins[i], OUTPUT);
    digitalWrite(activeOlfPins[i], LOW);
  }

  // TODO why does this sketch send scopePin high for a bit?
  digitalWrite(scopePin, HIGH);
  delay(500);
  digitalWrite(scopePin, LOW);
}

void loop() {
}
