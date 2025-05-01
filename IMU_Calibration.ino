#include <Wire.h>
#include <MPU6050.h>

// MPU6050 object
MPU6050 mpu;

void setup() {
  // Initialize serial port
  Serial.begin(9600);

  // Start I2C communication
  Wire.begin();

  // Initialize MPU6050 sensor
  mpu.initialize();

  // Test sensor connection
  if (!mpu.testConnection()) {
    Serial.println("MPU6050 connection failed!");
    while (1);  // Stop if connection fails
  }

  Serial.println("MPU6050 successfully connected.");
}

void loop() {
  // Get X, Y, Z acceleration values
  int16_t ax, ay, az;
  // Get X, Y, Z gyroscope values
  int16_t gx, gy, gz;

  // Retrieve acceleration and gyroscope data from MPU6050
  mpu.getAcceleration(&ax, &ay, &az);
  mpu.getRotation(&gx, &gy, &gz);

  // Send data via serial port
  Serial.print("X Accel: ");
  Serial.print(ax);
  Serial.print("\tY Accel: ");
  Serial.print(ay);
  Serial.print("\tZ Accel: ");
  Serial.println(az);

  Serial.print("X Gyro: ");
  Serial.print(gx);
  Serial.print("\tY Gyro: ");
  Serial.print(gy);
  Serial.print("\tZ Gyro: ");
  Serial.println(gz);

  delay(500);  // Wait 500ms
}
