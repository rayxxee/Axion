import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'dart:typed_data';

class ApiService {
  // Use 10.0.2.2 for Android emulator to connect to localhost:8000
  // Or put your local IP if testing on physical device
  static const String baseUrl = 'http://10.0.2.2:8000';

  static Future<Map<String, dynamic>> analyzeTextOrUrl(String inputType, String content) async {
    final response = await http.post(
      Uri.parse('$baseUrl/analyze'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'input_type': inputType,
        'content': content,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to analyze article: ${response.statusCode} - ${response.body}');
    }
  }

  static Future<Map<String, dynamic>> analyzePdf(String fileName, Uint8List fileBytes) async {
    var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/analyze/pdf'));
    request.files.add(http.MultipartFile.fromBytes(
      'file',
      fileBytes,
      filename: fileName,
      contentType: MediaType('application', 'pdf'),
    ));

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to analyze PDF: ${response.statusCode} - ${response.body}');
    }
  }

  static Future<Map<String, dynamic>> checkStatus(String runId) async {
    final response = await http.get(Uri.parse('$baseUrl/status/$runId'));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to check status');
    }
  }

  static Future<Map<String, dynamic>> getReport() async {
    final response = await http.get(Uri.parse('$baseUrl/report'));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get report');
    }
  }
}
