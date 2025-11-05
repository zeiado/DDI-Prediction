import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/interaction_provider.dart';
import '../widgets/drug_search_field.dart';
import '../test_data/sample_interaction.dart';
import 'result_screen.dart';
import 'history_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String _drugA = '';
  String _drugB = '';

  @override
  void initState() {
    super.initState();
    // Delay the server health check slightly to ensure proper widget mounting
    Future.delayed(const Duration(milliseconds: 100), () {
      if (mounted) {
        Provider.of<InteractionProvider>(context, listen: false).checkServerHealth();
      }
    });
  }

  void _swap() {
    setState(() {
      final temp = _drugA;
      _drugA = _drugB;
      _drugB = temp;
    });
  }

  @override
  Widget build(BuildContext context) {
    final prov = Provider.of<InteractionProvider>(context);

    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      body: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                // Header
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Expanded(
                      flex: 2,
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.medication, color: Theme.of(context).primaryColor, size: 28),
                          const SizedBox(width: 8),
                          const Text(
                            'DDI Predictor', 
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Expanded(
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Flexible(
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    Icons.circle,
                                    size: 8,
                                    color: prov.isServerOnline ? Colors.green : Colors.red,
                                  ),
                                  const SizedBox(width: 6),
                                  Flexible(
                                    child: Text(
                                      'Server Status: ${prov.isServerOnline ? "Online" : "Offline"}',
                                      style: const TextStyle(fontSize: 12),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.history),
                            onPressed: () => Navigator.push(
                              context,
                              MaterialPageRoute(builder: (_) => const HistoryScreen()),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 32),
                // Main title and subtitle
                const Text(
                  'Check Drug Interactions',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'AI-powered screening for healthcare professionals',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 24),
                // Card with search fields
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.grey.withAlpha((0.1 * 255).round()),
                        spreadRadius: 0,
                        blurRadius: 16,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(18.0),
                    child: Column(
                      children: [
                        DrugSearchField(
                          label: 'Drug A',
                          initialValue: _drugA,
                          onDrugSelected: (drug) => setState(() => _drugA = drug),
                        ),
                        const SizedBox(height: 16),
                        Row(
                          children: [
                            Expanded(child: Container()),
                            Container(
                              margin: const EdgeInsets.symmetric(horizontal: 12),
                              decoration: BoxDecoration(
                                color: Colors.blue.withAlpha((0.08 * 255).round()),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: IconButton(
                                icon: const Icon(Icons.swap_vert, color: Colors.blue),
                                onPressed: _swap,
                              ),
                            ),
                            Expanded(child: Container()),
                          ],
                        ),
                        const SizedBox(height: 16),
                        DrugSearchField(
                          label: 'Drug B',
                          initialValue: _drugB,
                          onDrugSelected: (drug) => setState(() => _drugB = drug),
                        ),
                        const SizedBox(height: 20),
                        SizedBox(
                          width: double.infinity,
                          child: FilledButton(
                            onPressed: prov.isLoading
                                ? null
                                : () async {
                                    if (_drugA.isEmpty || _drugB.isEmpty) {
                                      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter both drugs')));
                                      return;
                                    }
                                    await prov.checkInteraction(_drugA, _drugB);
                                    if (prov.error != null) {
                                      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(prov.error!)));
                                    } else if (prov.currentResult != null) {
                                      if (mounted) Navigator.push(context, MaterialPageRoute(builder: (_) => ResultScreen(result: prov.currentResult!)));
                                    }
                                  },
                            style: FilledButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 16),
                              backgroundColor: Theme.of(context).primaryColor,
                              foregroundColor: Colors.white,
                            ),
                            child: prov.isLoading
                                ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                                : const Text('Check Interaction', style: TextStyle(fontSize: 16)),
                          ),
                        ),
                        const SizedBox(height: 8),
                        SizedBox(
                          width: double.infinity,
                          child: OutlinedButton(
                            onPressed: () {
                              // Preview a sample result to inspect the ResultScreen UI
                              final sample = sampleWarfarinAspirin();
                              Navigator.push(context, MaterialPageRoute(builder: (_) => ResultScreen(result: sample)));
                            },
                            child: const Text('Preview sample result'),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 28),
                // Quick stats
                Row(
                  children: [
                    _buildStatCard('Total Checks', prov.history.length.toString(), Icons.analytics_outlined, Colors.blue),
                    const SizedBox(width: 12),
                    _buildStatCard('Interactions Found', prov.history.where((e) => e.interactionExists).length.toString(), Icons.warning_amber_outlined, Colors.orange),
                    const SizedBox(width: 12),
                    _buildStatCard('Safe Combinations', prov.history.where((e) => !e.interactionExists).length.toString(), Icons.check_circle_outline, Colors.green),
                  ],
                ),
                const SizedBox(height: 20),
                // Disclaimer
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: Colors.blue.withAlpha((0.06 * 255).round()),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: const [
                      Icon(Icons.info_outline, color: Colors.blue),
                      SizedBox(width: 12),
                      Expanded(
                        child: Text('For Healthcare Professionals Only. Not for patient self-diagnosis. Consult a physician.'),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.grey.withAlpha((0.06 * 255).round()),
              blurRadius: 12,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(height: 8),
            Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text(title, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
          ],
        ),
      ),
    );
  }
}
