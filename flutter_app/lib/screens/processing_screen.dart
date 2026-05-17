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
        }
      } catch (e) {
        // Just retry on error
        debugPrint('Poll error: $e');
      }
      
      // Timeout after 2 mins
      if (_secondsElapsed > 120) {
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
    return Scaffold(
      appBar: AppBar(title: const Text('Processing')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 24),
            const Text(
              'Antigravity Agents are working...',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Status: $_status',
              style: const TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 8),
            Text('${_secondsElapsed}s elapsed'),
          ],
        ),
      ),
    );
  }
}
