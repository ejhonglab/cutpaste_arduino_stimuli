
// TODO make all floats doubles? make most integral (milli/micro)seconds?
// TODO annotate these with units
const float odorPulseLen = 2;
const float odorStartInterval= 10;
const float interOdorInterval= 30;
const float odorEndInterval = 30; 

const int ITI = 60;
const int blockNum = 3;
const int odorsPerBlock = 3;

const float scopeLen = (odorsPerBlock * odorPulseLen)
                        + odorStartInterval + odorEndInterval 
                        + (odorsPerBlock-1)*interOdorInterval;

const unsigned long mirrorDelay = 1000;  //padding time for flipper mirror in milliseconds

// Pin assignments
// TODO what is the mirror pin?
// TODO olfDispPin?
// TODO mirrorPin?
const int scopePin = 46;
const int olfDispPin = 47; 
const int flowPin=48;
const int mirrorPin = 49;

const int activeOlfPins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 31};
const int numPins = sizeof(activeOlfPins)/sizeof(int); 

//const int channelA[] = {2,7,5,3,6,4, 3,4,5,2,6,7, 3,4,7,5,2,6};
const int channelA[] = {2,2,2, 2,2,2, 2,2,2};
const int channelB[] = {2,3,3, 3,3,3, 3,3,3};

const int base = sizeof(channelA)/sizeof(int);

int nstim;

void setup() {
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
  
  // initialize digital pin as an output, set to low
  pinMode(scopePin, OUTPUT);
  digitalWrite(scopePin, LOW);
  
  pinMode(olfDispPin, OUTPUT);
  digitalWrite(olfDispPin, LOW);

  pinMode(mirrorPin, OUTPUT);
  digitalWrite(mirrorPin, LOW);
  
  pinMode(flowPin, OUTPUT);
  digitalWrite(flowPin, LOW);

  for (int i=0; i < numPins; i++){
    pinMode(activeOlfPins[i], OUTPUT);
    digitalWrite(activeOlfPins[i], LOW);
  }
  
  nstim = 0;
  delay(10*1000);
}

void loop() {
  int pinA;
  int pinB;

  for (int block=0; block<blockNum; block++){
    
      Serial.print(block+1);
      Serial.print(": \t");
      
      digitalWrite(mirrorPin, HIGH);  // flip mirror
      delay(mirrorDelay);
      digitalWrite(scopePin, HIGH) ;  // scope trigger on

      for (int pulse=0; pulse<odorsPerBlock; pulse++){
        // TODO remove mod / base. it shouldn't be doing anything.
        pinA = channelA[nstim % base];
        pinB = channelB[nstim % base];

        if (pulse == 0) {
          delay((unsigned long) (odorStartInterval * 1000));

        } else if (pulse > 0) {
          delay((unsigned long) (interOdorInterval * 1000));
        }

        Serial.print("(");
        Serial.print(pinA);
        Serial.print(", ");
        Serial.print(pinB);
        Serial.print(")");

        // Odor pulse
        digitalWrite(flowPin, HIGH);
        digitalWrite(pinA, HIGH);
        digitalWrite(pinB, HIGH);
        digitalWrite(olfDispPin, HIGH);

        delay((unsigned long) (odorPulseLen * 1000)); 

        digitalWrite(flowPin, LOW);
        digitalWrite(pinA, LOW);
        digitalWrite(pinB, LOW);
        digitalWrite(olfDispPin, LOW);

        nstim = nstim + 1;
      }
      Serial.println(" ");
      delay((unsigned long) (odorEndInterval * 1000)); 
      digitalWrite(scopePin, LOW);  // scope trigger off
      delay(mirrorDelay);
      digitalWrite(mirrorPin, LOW); // close mirror

      // TODO note casting is different here (think it gets precedence)
      // be consistent
      delay(((unsigned long) ITI * 1000) - 2 * mirrorDelay);
  }
}

