import 'package:flutter/material.dart';

class ResultScreen extends StatelessWidget {
  final Map<String, dynamic> report;
  const ResultScreen({super.key, required this.report});

  @override
  Widget build(BuildContext context) {
    final insight = report['insight_card'] ?? {};
    final metrics = report['impact_metrics'] ?? {};
    final actions = report['actions'] ?? [];
    final beforeState = report['before_state'] ?? [];
    final afterState = report['after_state'] ?? [];
    final executionLog = report['execution_log'] ?? [];
    final notificationDraft = report['notification_draft'] ?? {};
    final stateChangeSummary = report['state_change_summary'];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Analysis Result'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // State Change Banner
            if (stateChangeSummary != null)
              Container(
                margin: const EdgeInsets.only(bottom: 16),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.1),
                  border: Border.all(color: Colors.green.withOpacity(0.3)),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.check_circle, color: Colors.green),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        stateChangeSummary,
                        style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
              ),

            // Insight Card
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      insight['headline'] ?? 'Analysis Complete',
                      style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Chip(
                          label: Text(
                            (insight['severity'] ?? 'INFO').toString().toUpperCase(),
                            style: const TextStyle(color: Colors.white, fontSize: 12),
                          ),
                          backgroundColor: _getSeverityColor(insight['severity']),
                        ),
                        const SizedBox(width: 8),
                        Chip(
                          label: Text((insight['topic'] ?? 'GENERAL').toString().toUpperCase(), style: const TextStyle(fontSize: 12)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(
                      insight['one_line_insight'] ?? insight['one_liner'] ?? '',
                      style: const TextStyle(fontSize: 16),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),

            // Metrics
            Row(
              children: [
                _buildMetricCard(
                  'Monthly Impact',
                  metrics['monthly_revenue_impact_pkr']?.toString() ?? 'N/A',
                  Icons.monetization_on,
                  Colors.blue,
                ),
                const SizedBox(width: 12),
                _buildMetricCard(
                  'Margin Change',
                  '${metrics['margin_change_pct'] ?? 0}%',
                  Icons.percent,
                  (metrics['margin_change_pct'] ?? 0) < 0 ? Colors.red : Colors.green,
                ),
              ],
            ),

            const SizedBox(height: 24),
            const Text('Recommended Actions', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),

            // Actions list
            ...actions.map<Widget>((action) {
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                    child: Text('${action['rank'] ?? '-'}'),
                  ),
                  title: Text(action['title'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(action['expected_outcome'] ?? ''),
                  trailing: action['simulate'] == true 
                    ? const Chip(label: Text('Simulated', style: TextStyle(fontSize: 10)), backgroundColor: Colors.greenAccent)
                    : null,
                ),
              );
            }).toList(),
            
            const SizedBox(height: 24),
            const Text('Action Simulation Results', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),

            // Before / After Table
            if ((beforeState is List && beforeState.isNotEmpty) || (beforeState is Map && beforeState.isNotEmpty))
              _buildBeforeAfterTable(beforeState, afterState),

            const SizedBox(height: 24),

            // Execution Logs
            if (executionLog is List && executionLog.isNotEmpty)
              _buildExecutionLog(executionLog),

            const SizedBox(height: 24),

            // Notifications
            if (notificationDraft is Map && notificationDraft.isNotEmpty)
              _buildNotificationPreview(notificationDraft),

            const SizedBox(height: 24),
            
            ElevatedButton.icon(
              onPressed: () => Navigator.popUntil(context, (route) => route.isFirst),
              icon: const Icon(Icons.refresh),
              label: const Text('Analyze Another Article'),
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildBeforeAfterTable(dynamic beforeState, dynamic afterState) {
    List<dynamic> beforeList = beforeState is List ? beforeState : beforeState.values.toList();
    List<dynamic> afterList = afterState is List ? afterState : afterState.values.toList();

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Pricing State Change (Before vs After)', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                columns: const [
                  DataColumn(label: Text('Product')),
                  DataColumn(label: Text('Before (PKR)')),
                  DataColumn(label: Text('After (PKR)')),
                ],
                rows: beforeList.map<DataRow>((bItem) {
                  final name = bItem['name'] ?? bItem['id'] ?? 'Unknown';
                  final bPrice = bItem['total_price_pkr'] ?? bItem['price_pkr'] ?? '-';
                  
                  // Find corresponding after item
                  final aItem = afterList.firstWhere(
                    (a) => (a['name'] ?? a['id']) == name,
                    orElse: () => {},
                  );
                  final aPrice = aItem['total_price_pkr'] ?? aItem['price_pkr'] ?? '-';

                  return DataRow(cells: [
                    DataCell(Text(name.toString())),
                    DataCell(Text(bPrice.toString())),
                    DataCell(Text(aPrice.toString(), style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold))),
                  ]);
                }).toList(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildExecutionLog(List<dynamic> logs) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Antigravity Execution Log', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Container(
              height: 200,
              decoration: BoxDecoration(
                color: Colors.black87,
                borderRadius: BorderRadius.circular(8),
              ),
              child: ListView.builder(
                padding: const EdgeInsets.all(8),
                itemCount: logs.length,
                itemBuilder: (context, index) {
                  final log = logs[index];
                  final timestamp = log['timestamp']?.toString().substring(11, 19) ?? '';
                  final agent = log['agent'] ?? 'System';
                  final action = log['action'] ?? '';
                  
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 4.0),
                    child: RichText(
                      text: TextSpan(
                        style: const TextStyle(fontFamily: 'monospace', fontSize: 12, color: Colors.white70),
                        children: [
                          TextSpan(text: '[$timestamp] ', style: const TextStyle(color: Colors.grey)),
                          TextSpan(text: '[$agent] ', style: const TextStyle(color: Colors.blueAccent)),
                          TextSpan(text: action, style: const TextStyle(color: Colors.white)),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotificationPreview(Map<dynamic, dynamic> notif) {
    final email = notif['email'];
    final sms = notif['sms'];
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text('Simulated Notifications', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        if (email != null)
          Card(
            color: Colors.blue.shade50,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.email, color: Colors.blue),
                      const SizedBox(width: 8),
                      Expanded(child: Text('Subject: ${email['subject']}', style: const TextStyle(fontWeight: FontWeight.bold))),
                    ],
                  ),
                  const Divider(),
                  Text(email['body'] ?? '', style: const TextStyle(fontSize: 14)),
                ],
              ),
            ),
          ),
        if (sms != null)
          Card(
            color: Colors.green.shade50,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.sms, color: Colors.green),
                      SizedBox(width: 8),
                      Text('SMS Draft', style: TextStyle(fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const Divider(),
                  Text(sms['body'] ?? '', style: const TextStyle(fontSize: 14)),
                ],
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildMetricCard(String title, String value, IconData icon, Color color) {
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              Icon(icon, color: color, size: 32),
              const SizedBox(height: 8),
              Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 4),
              Text(title, style: const TextStyle(fontSize: 12, color: Colors.grey)),
            ],
          ),
        ),
      ),
    );
  }

  Color _getSeverityColor(String? severity) {
    switch (severity?.toLowerCase()) {
      case 'low': return Colors.green;
      case 'medium': return Colors.orange;
      case 'high': return Colors.deepOrange;
      case 'critical': return Colors.red;
      default: return Colors.grey;
    }
  }
}
