import 'dart:convert';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'dart:typed_data';

class ApiService {
  static const String baseUrl = 'https://axion-backend-133838314315.us-central1.run.app';
  static const Duration _timeout = Duration(seconds: 30);

  /// Wraps HTTP calls with timeout and connection error handling
  static Future<http.Response> _safeGet(String path) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl$path'),
      ).timeout(_timeout);
      return response;
    } on TimeoutException {
      throw Exception('Request timed out. Backend may be cold-starting, try again.');
    } catch (e) {
      if (e.toString().contains('SocketException') ||
          e.toString().contains('Connection refused') ||
          e.toString().contains('Network is unreachable') ||
          e.toString().contains('Failed host lookup')) {
        throw Exception('No internet connection. Please check your network.');
      }
      rethrow;
    }
  }

  static Future<http.Response> _safePost(String path, {Map<String, String>? headers, String? body}) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl$path'),
        headers: headers,
        body: body,
      ).timeout(_timeout);
      return response;
    } on TimeoutException {
      throw Exception('Request timed out. Backend may be cold-starting, try again.');
    } catch (e) {
      if (e.toString().contains('SocketException') ||
          e.toString().contains('Connection refused') ||
          e.toString().contains('Network is unreachable') ||
          e.toString().contains('Failed host lookup')) {
        throw Exception('No internet connection. Please check your network.');
      }
      rethrow;
    }
  }

  static Future<Map<String, dynamic>> analyzeTextOrUrl(String inputType, String content) async {
    final response = await _safePost(
      '/analyze',
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
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/analyze/pdf'));
      request.files.add(http.MultipartFile.fromBytes(
        'file',
        fileBytes,
        filename: fileName,
        contentType: MediaType('application', 'pdf'),
      ));

      final streamedResponse = await request.send().timeout(_timeout);
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to analyze PDF: ${response.statusCode} - ${response.body}');
      }
    } on TimeoutException {
      throw Exception('PDF upload timed out. Try again.');
    } catch (e) {
      if (e.toString().contains('SocketException') ||
          e.toString().contains('Connection refused')) {
        throw Exception('No internet connection. Please check your network.');
      }
      rethrow;
    }
  }

  static Future<Map<String, dynamic>> checkStatus(String runId) async {
    final response = await _safeGet('/status/$runId');
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to check status: ${response.statusCode}');
    }
  }

  static Future<Map<String, dynamic>> getReport() async {
    final response = await _safeGet('/report');
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get report: ${response.statusCode}');
    }
  }

  /// Quick connectivity check — hits /health endpoint
  static Future<bool> testConnection() async {
    try {
      final response = await _safeGet('/health');
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
