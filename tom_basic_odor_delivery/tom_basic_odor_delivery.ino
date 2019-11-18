
const float odor_pulse_s = 1;
const float before_odor_s = 10;
const float after_odor_s = 45;
// TODO should this also be a float?
const int between_block_s = 30;

const unsigned long mirror_delay_ms = 1000;  //padding time for flipper mirror in milliseconds

// pin and odor assignments

const int scope_pin = 46;
const int olf_disp_pin = 47; 
const int flow_pin = 48;
const int mirror_pin = 49;
const int teflon_manifold_switcher = 12;
const int other_manifold_pin = 11;

const int start_low_pins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
const int num_low_pins = sizeof(start_low_pins) / sizeof(int);

/*
const int block_num = 1;
const int odors_per_block = 1;
const int channelA[] = {4};
*/

const int block_num = 3;
const int odors_per_block = 7;
const int channelA[] = {
 9,6,8,5,4,3,10, 3,4,10,9,5,6,8, 6,10,3,4,5,9,8
};


const float total_block_s = odors_per_block * (odor_pulse_s + after_odor_s) + before_odor_s;

const int base = sizeof(channelA) / sizeof(int);

void flip_mirror() {
  digitalWrite(mirror_pin, HIGH);
  delay(500);
  digitalWrite(mirror_pin, LOW);
}


/*state variables--------------------------------------------------------------------------*/

int nstim;
int pinA;

void setup() {
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps

  // inbetween_block_salize digital pin as an output, set to low
  pinMode(scope_pin, OUTPUT);
  digitalWrite(scope_pin, LOW);
  
  pinMode(olf_disp_pin, OUTPUT);
  digitalWrite(olf_disp_pin, LOW);

  pinMode(mirror_pin, OUTPUT);
  digitalWrite(mirror_pin, LOW);
  
  pinMode(flow_pin, OUTPUT);
  digitalWrite(flow_pin, LOW);

  for (int i=0; i < num_low_pins; i++){
    pinMode(start_low_pins[i], OUTPUT);
    digitalWrite(start_low_pins[i], LOW);
  }
  
  nstim = 0;
  delay(5 * 1000);

  for (int block = 0; block < block_num; block++) {
      Serial.print(block + 1);
      Serial.print(": \t");
      
      flip_mirror();
      delay(500);
      digitalWrite(scope_pin, HIGH) ;  // scope trigger on

      for (int pulse = 0; pulse < odors_per_block; pulse++) {
        pinA = channelA[nstim % base];
        if (pinA == other_manifold_pin) {
          digitalWrite(teflon_manifold_switcher, HIGH);
        }
        
        if (pulse == 0) {
          delay((unsigned long) (before_odor_s * 1000));
        }
        
        Serial.print(pinA);
        Serial.print(", ");
        
        // odor pulse
        digitalWrite(flow_pin, HIGH);
        digitalWrite(pinA, HIGH);
        digitalWrite(olf_disp_pin, HIGH);
        delay((unsigned long) (odor_pulse_s * 1000)); 
        digitalWrite(flow_pin, LOW);
        digitalWrite(pinA, LOW);
        digitalWrite(olf_disp_pin, LOW);

        delay((unsigned long) (after_odor_s * 1000)); 

        digitalWrite(teflon_manifold_switcher, LOW);

        nstim = nstim + 1;
      }
      Serial.println(" ");
      digitalWrite(scope_pin, LOW);  // scope trigger off
      
      delay(500);
      flip_mirror();

      // TODO if parens arent mul by 1000 was necessary before casts above, wrong here. be consistent.
      delay(((unsigned long) between_block_s * 1000) - 2 * mirror_delay_ms);
  }
  Serial.println("DONE");
}

void loop() {
}

