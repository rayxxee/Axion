import 'package:flutter_test/flutter_test.dart';
import 'package:axion_app/main.dart';

void main() {
  testWidgets('App renders InputScreen', (WidgetTester tester) async {
    await tester.pumpWidget(const AxionApp());
    expect(find.text('Axion Analyzer'), findsOneWidget);
  });
}
