#include <ESP8266WiFi.h>
#include <Servo.h>

WiFiClient client;
WiFiServer server(80);
String request;          // Declare request variable outside the if block
String print, image, cause, cure;

void setup() {
  Serial.begin(9600);
  WiFi.mode(WIFI_STA);
  WiFi.begin("SSID", "PASSWORD");
  Serial.println("connecting to wifi! ");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(500);
  }
  Serial.println(' ');
  Serial.print("IP Address = ");
  Serial.println(WiFi.localIP());
  Serial.print("MAC Address = ");
  Serial.println(WiFi.macAddress());
  server.begin();
}

void loop() {
  client = server.available();
  if (client) {
    request = client.readStringUntil('\n');
    Serial.println(request);
    request.trim();

    if (request == "Healthy" || request == "Bacterial Spot" || request == "Early Blight" || request == "Late Blight" || request == "Leaf Mold" || request == "Septoria Leaf Spot" || request == "Target Spot"){
      print = request;
    }
    if (print == "Healthy"){
      image = "https://github.com/Chaotic-VRBlue/Major-Project/blob/main/Tomato%20Leaf%20Disease%20Detection/Success%20Leaves/Healthy%20image%20(151).JPG?raw=true";
      cause = "No disease detected. Your tomato leaves are healthy.";
      cure = "No cure needed. Maintain proper plant care to prevent diseases.";
    }
    else if (print == "Bacterial Spot"){
      image = "https://github.com/Chaotic-VRBlue/Major-Project/blob/main/Tomato%20Leaf%20Disease%20Detection/Success%20Leaves/Bacterial%20Spot%20image%20(87).JPG?raw=true";
      cause = "Caused by the bacteria Xanthomonas campestris pv. vesicatoria. It spreads through contaminated water and soil.";
      cure = "Remove affected leaves, apply copper-based fungicides, and practice crop rotation.";
    }
    else if (print == "Early Blight"){
      image = "https://github.com/Chaotic-VRBlue/Major-Project/blob/main/Tomato%20Leaf%20Disease%20Detection/Success%20Leaves/Early%20Blight%20image%20(766).JPG?raw=true";
      cause = "Caused by the fungus Alternaria solani. It spreads through contaminated seeds and soil.";
      cure = "Remove affected leaves, apply fungicides, and practice crop rotation.";
    }
    else if (print == "Late Blight"){
      image = "https://github.com/Chaotic-VRBlue/Major-Project/blob/main/Tomato%20Leaf%20Disease%20Detection/Success%20Leaves/Late%20Blight.jpg?raw=true";
      cause = "Caused by the fungus Phytophthora infestans. It thrives in cool and moist conditions.";
      cure = "Remove affected leaves, apply fungicides, and avoid overhead irrigation.";
    }
    else if (print == "Leaf Mold"){
      image = "https://github.com/Chaotic-VRBlue/Major-Project/blob/main/Tomato%20Leaf%20Disease%20Detection/Success%20Leaves/Leaf%20Mold.jpeg?raw=true";
      cause = "Caused by the fungus Fulvia fulva. It thrives in high humidity and cool temperatures.";
      cure = "Remove affected leaves, improve air circulation, and apply fungicides.";
    }
    else if (print == "Septoria Leaf Spot"){
      image = "https://github.com/Chaotic-VRBlue/Major-Project/blob/main/Tomato%20Leaf%20Disease%20Detection/Success%20Leaves/Septoria%20Leaf%20Spot.jpg?raw=true";
      cause = "Caused by the fungus Septoria lycopersici. It spreads through water splash and contaminated soil.";
      cure = "Remove affected leaves, apply fungicides, and practice crop rotation.";
    }
    else if (print == "Target Spot"){
      image = "https://github.com/Chaotic-VRBlue/Major-Project/blob/main/Tomato%20Leaf%20Disease%20Detection/Success%20Leaves/Target%20Spot%20image%20(1378).JPG?raw=true";
      cause = "Caused by the fungus Corynespora cassiicola. It spreads through infected seeds and soil.";
      cure = "Remove affected leaves, apply fungicides, and practice crop rotation.";
    }
  }
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type:L text/html");
  client.println("");
  client.println("<!DOCTYPE HTML>");
  client.println("<html>");
  client.println("<head>");
  client.println("<title>ESP8266 Web Server</title>");
  client.println("</head>");
  client.println("<body>");
  client.print("<h1>String sent from Raspberry Pi:</h1>");
  client.print("<img src="+ image + ">");
  client.print("<p>" + print + "</p>");
  client.print("<p>" + cause + "</p>");
  client.print("<p>" + cure + "</p>");
  
  client.println("<script>");
  client.println("function refreshPage() { location.reload(); }");
  client.println("setInterval(refreshPage, 5000);");
  client.println("</script>");

  client.println("</body>");
  client.println("</html>");
}
