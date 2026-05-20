import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../api_service.dart';
import 'processing_screen.dart';

class InputScreen extends StatefulWidget {
  const InputScreen({super.key});

  @override
  State<InputScreen> createState() => _InputScreenState();
}

class _InputScreenState extends State<InputScreen> {
  final TextEditingController _textController = TextEditingController();
  bool _isLoading = false;
  String _activeTab = 'text'; // 'text', 'url', 'pdf'
  PlatformFile? _selectedPdf;
  bool? _isConnected; // null = checking, true = connected, false = failed

  @override
  void initState() {
    super.initState();
    _checkConnection();
  }

  Future<void> _checkConnection() async {
    final ok = await ApiService.testConnection();
    if (mounted) setState(() => _isConnected = ok);
  }

  final List<Map<String, String>> _demos = [
    {
      'label': 'SBP +200bps',
      'text': 'KARACHI: The State Bank of Pakistan (SBP) has announced an increase in the policy rate by 200 basis points, bringing the key interest rate to 19.5%. The Monetary Policy Committee (MPC) cited persistent inflationary pressures and external sector vulnerabilities as key factors behind the decision.'
    },
    {
      'label': 'Petrol +18%',
      'text': 'ISLAMABAD: The Oil and Gas Regulatory Authority (OGRA) has notified an increase in petrol prices by Rs 52.36 per liter, effective immediately. The new price of petrol is Rs 350.86 per liter, up from Rs 298.50.'
    },
  ];

  Future<void> _submit() async {
    if (_activeTab == 'pdf') {
      if (_selectedPdf == null || _selectedPdf!.bytes == null) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please select a valid PDF file')));
        return;
      }
    } else {
      if (_textController.text.trim().length < 10) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter at least 10 characters')));
        return;
      }
    }

    setState(() => _isLoading = true);

    try {
      Map<String, dynamic> result;
      if (_activeTab == 'pdf') {
        result = await ApiService.analyzePdf(_selectedPdf!.name, _selectedPdf!.bytes!);
      } else {
        result = await ApiService.analyzeTextOrUrl(_activeTab, _textController.text.trim());
      }
      
      if (!mounted) return;
      
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => ProcessingScreen(runId: result['run_id']),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _pickPdf() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
      withData: true,
    );

    if (result != null) {
      setState(() {
        _selectedPdf = result.files.first;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Axion Analyzer'),
        centerTitle: true,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Connection status banner
            if (_isConnected == false)
              Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.1),
                  border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.cloud_off, color: Colors.red, size: 20),
                    const SizedBox(width: 8),
                    const Expanded(child: Text('Cannot reach backend. Check internet.', style: TextStyle(color: Colors.red, fontSize: 13))),
                    IconButton(
                      icon: const Icon(Icons.refresh, size: 18),
                      onPressed: () {
                        setState(() => _isConnected = null);
                        _checkConnection();
                      },
                    ),
                  ],
                ),
              ),
            if (_isConnected == null)
              const Padding(
                padding: EdgeInsets.only(bottom: 12),
                child: LinearProgressIndicator(),
              ),
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: 'text', icon: Icon(Icons.text_snippet), label: Text('Text')),
                ButtonSegment(value: 'url', icon: Icon(Icons.link), label: Text('URL')),
                ButtonSegment(value: 'pdf', icon: Icon(Icons.picture_as_pdf), label: Text('PDF')),
              ],
              selected: {_activeTab},
              onSelectionChanged: (Set<String> newSelection) {
                setState(() {
                  _activeTab = newSelection.first;
                  _textController.clear();
                  _selectedPdf = null;
                });
              },
            ),
            const SizedBox(height: 24),
            
            if (_activeTab == 'text' || _activeTab == 'url')
              Expanded(
                child: TextField(
                  controller: _textController,
                  maxLines: null,
                  expands: true,
                  textAlignVertical: TextAlignVertical.top,
                  decoration: InputDecoration(
                    hintText: _activeTab == 'text' ? 'Paste news article here...' : 'https://...',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
              
            if (_activeTab == 'pdf')
              Expanded(
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.picture_as_pdf, size: 64, color: Colors.grey.shade400),
                      const SizedBox(height: 16),
                      if (_selectedPdf != null) ...[
                        Text(_selectedPdf!.name, style: const TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        Text('${(_selectedPdf!.size / 1024).toStringAsFixed(1)} KB'),
                        const SizedBox(height: 16),
                      ],
                      ElevatedButton.icon(
                        onPressed: _pickPdf,
                        icon: const Icon(Icons.upload_file),
                        label: Text(_selectedPdf == null ? 'Select PDF' : 'Change PDF'),
                      )
                    ],
                  ),
                ),
              ),
              
            if (_activeTab == 'text') ...[
              const SizedBox(height: 16),
              const Text('Demo Scenarios:', style: TextStyle(fontSize: 12, color: Colors.grey)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: _demos.map((demo) {
                  return ActionChip(
                    label: Text(demo['label']!),
                    onPressed: () {
                      _textController.text = demo['text']!;
                    },
                  );
                }).toList(),
              ),
            ],
            
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: _isLoading ? null : _submit,
              icon: _isLoading 
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                : const Icon(Icons.bolt),
              label: Text(_isLoading ? 'Processing...' : 'Run Analysis Pipeline'),
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
