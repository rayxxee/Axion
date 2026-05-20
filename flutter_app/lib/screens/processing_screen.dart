import 'dart:async';
import 'package:flutter/material.dart';
import '../api_service.dart';
import 'result_screen.dart';

class ProcessingScreen extends StatefulWidget {
  final String runId;
  const ProcessingScreen({super.key, required this.runId});

  @override
  State<ProcessingScreen> createState() => _ProcessingScreenState();
}

class _ProcessingScreenState extends State<ProcessingScreen> {
  String _status = 'pending';
  Timer? _timer;
  int _secondsElapsed = 0;

  @override
  void initState() {
    super.initState();
    _startPolling();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _startPolling() {
    _timer = Timer.periodic(const Duration(seconds: 2), (timer) async {
      if (!mounted) return;
      setState(() => _secondsElapsed += 2);

      try {
        final statusData = await ApiService.checkStatus(widget.runId);
        final status = statusData['status'];
        
        if (mounted) {
          setState(() => _status = status ?? 'processing');
        }

        if (status == 'complete') {
          timer.cancel();
          _fetchReport();
        } else if (status == 'error') {
          timer.cancel();
          if (mounted) {
            setState(() => _status = 'error');
            final errorMsg = statusData['error_message'] ?? 'Pipeline failed';
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(errorMsg)));
          }
        }
      } catch (e) {
        // Just retry on error
        debugPrint('Poll error: $e');
      }
      
      // Timeout after 4 mins
      if (_secondsElapsed > 240) {
        timer.cancel();
        if (mounted) {
          setState(() => _status = 'error');
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Pipeline timed out')));
        }
      }
    });
  }

  Future<void> _fetchReport() async {
    try {
      final report = await ApiService.getReport();
      if (!mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => ResultScreen(report: report),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => _status = 'error');
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    }
  }

  @override
  Widget build(BuildContext context) {
    String agentName = '';
    String actionText = _status;

    if (_status.contains(':')) {
      final parts = _status.split(':');
      agentName = parts[0].trim();
      actionText = parts.sublist(1).join(':').trim();
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Processing')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 80,
                    height: 80,
                    child: CircularProgressIndicator(
                      strokeWidth: 6,
                      color: Theme.of(context).colorScheme.primary.withOpacity(0.5),
                    ),
                  ),
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.primary.withOpacity(0.2),
                      shape: BoxShape.circle,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 32),
              Text(
                agentName.isNotEmpty ? 'Agent Active: $agentName' : 'Pipeline Running...',
                style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(30),
                  border: Border.all(color: Theme.of(context).colorScheme.primary.withOpacity(0.3)),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    SizedBox(
                      width: 12,
                      height: 12,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Flexible(
                      child: Text(
                        actionText.isNotEmpty ? actionText : 'Initializing Antigravity pipeline...',
                        style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              Text(
                '${_secondsElapsed}s elapsed',
                style: const TextStyle(color: Colors.grey),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
