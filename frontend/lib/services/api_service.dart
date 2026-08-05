// lib/services/api_service.dart
// HTTP client for the StartRightDay FastAPI backend.
// All errors are surfaced as typed exceptions with user-friendly messages.

import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/recommendation_result.dart';
import '../models/user_birth_details.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;

  const ApiException(this.message, {this.statusCode});

  @override
  String toString() => 'ApiException($statusCode): $message';
}

class ApiService {
  // Change this to your deployed backend URL for production
  static const String _baseUrl = 'http://10.0.2.2:8000'; // Android emulator
  // static const String _baseUrl = 'http://localhost:8000'; // iOS simulator / web

  static const Duration _timeout = Duration(seconds: 30);

  Future<RecommendationResult> recommend(UserBirthDetails details) async {
    final uri = Uri.parse('$_baseUrl/api/v1/recommend');
    final body = jsonEncode(details.toJson());

    try {
      final response = await http
          .post(
            uri,
            headers: {'Content-Type': 'application/json'},
            body: body,
          )
          .timeout(_timeout);

      return _handleResponse(response);
    } on SocketException {
      throw const ApiException(
        'Cannot connect to server. Please check your internet connection and try again.',
      );
    } on HttpException catch (e) {
      throw ApiException('Network error: ${e.message}');
    } on FormatException {
      throw const ApiException('Received an unexpected response from server.');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Unexpected error: $e');
    }
  }

  RecommendationResult _handleResponse(http.Response response) {
    switch (response.statusCode) {
      case 200:
        try {
          final json = jsonDecode(response.body) as Map<String, dynamic>;
          return RecommendationResult.fromJson(json);
        } on FormatException {
          throw const ApiException('Invalid response format from server.');
        }

      case 422:
        // Pydantic validation error or ValueError from domain logic
        try {
          final json = jsonDecode(response.body) as Map<String, dynamic>;
          final detail = json['detail'];
          final message = detail is String
              ? detail
              : 'Invalid input. Please check your details and try again.';
          throw ApiException(message, statusCode: 422);
        } catch (e) {
          if (e is ApiException) rethrow;
          throw const ApiException(
            'Validation error. Please check your input.',
            statusCode: 422,
          );
        }

      case 500:
        throw const ApiException(
          'Server error. Please try again in a moment.',
          statusCode: 500,
        );

      default:
        throw ApiException(
          'Unexpected response (${response.statusCode}). Please try again.',
          statusCode: response.statusCode,
        );
    }
  }
}
