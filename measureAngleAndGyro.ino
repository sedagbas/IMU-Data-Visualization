#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

// Hassasiyet için dönüştürme katsayısı (±2g için)
const float accel_scale = 16384.0;

// Kalibrasyon için offset değerleri
const float ax_offset = 0.210;  // Örnek X ivme offseti
const float ay_offset = 0.008;  // Örnek Y ivme offseti
const float az_offset = 1.035;  // Örnek Z ivme offseti

const float gx_offset = -619;   // Örnek X jiroskop offseti
const float gy_offset = -336;   // Örnek Y jiroskop offseti
const float gz_offset = -70;    // Örnek Z jiroskop offseti

// LED pinleri
const int greenLED = 13;
const int redLED = 12;

void setup() {
  Serial.begin(9600);  // Seri haberleşmeyi başlat
  Wire.begin();
  mpu.initialize();  // MPU6050 sensörünü başlat
  
  // LED pinlerini çıkış olarak ayarla
  pinMode(greenLED, OUTPUT);
  pinMode(redLED, OUTPUT);

  if (!mpu.testConnection()) {
    Serial.println("MPU6050 not connected!");
    while (1);  // Sensör bağlantısı başarısızsa, bekle
  }
  
  // Başlangıçta kırmızı LED'i yak
  digitalWrite(greenLED, LOW);
  digitalWrite(redLED, HIGH);
}

void loop() {
  // X, Y, Z ivme ve jiroskop verilerini al
  int16_t ax, ay, az;
  int16_t gx, gy, gz;

  mpu.getAcceleration(&ax, &ay, &az);
  mpu.getRotation(&gx, &gy, &gz);
  
  // İvme değerlerini g cinsine dönüştür ve offset uygula
  float ax_g = (ax / accel_scale) - ax_offset;
  float ay_g = (ay / accel_scale) - ay_offset;
  float az_g = (az / accel_scale) - az_offset;

  // Jiroskop verilerine offset uygula
  float gx_dps = gx - gx_offset;
  float gy_dps = gy - gy_offset;
  float gz_dps = gz - gz_offset;

  // Seri port üzerinden veri gönder
  Serial.print(ax_g, 6);  // 6 ondalıklı hassasiyetle yazdır
  Serial.print(",");
  Serial.print(ay_g, 6);
  Serial.print(",");
  Serial.print(az_g, 6);
  Serial.print(",");
  Serial.print(gx_dps);  // X jiroskop verisi
  Serial.print(",");
  Serial.print(gy_dps);  // Y jiroskop verisi
  Serial.print(",");
  Serial.println(gz_dps);  // Z jiroskop verisi

  // Verilerin sıfırdan farklı olup olmadığını kontrol et
  if (ax_g != 0.0 || ay_g != 0.0 || az_g != 0.0 || gx_dps != 0.0 || gy_dps != 0.0 || gz_dps != 0.0) {
    // Veriler sıfırdan farklıysa yeşil LED'i yak, kırmızı LED'i söndür
    digitalWrite(greenLED, HIGH);
    digitalWrite(redLED, LOW);
  } else {
    // Veriler sıfırsa kırmızı LED'i yak, yeşil LED'i söndür
    digitalWrite(greenLED, LOW);
    digitalWrite(redLED, HIGH);
  }

  delay(3000);  // 3 saniye bekle
}