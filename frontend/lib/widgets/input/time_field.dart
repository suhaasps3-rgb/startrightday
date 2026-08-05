// lib/widgets/input/time_field.dart
import 'package:flutter/material.dart';
import '../../theme/app_theme.dart';

class TimeField extends StatelessWidget {
  final String label;
  final TimeOfDay? selectedTime;
  final ValueChanged<TimeOfDay> onTimeSelected;
  final String? errorText;

  const TimeField({
    super.key,
    required this.label,
    required this.selectedTime,
    required this.onTimeSelected,
    this.errorText,
  });

  String _format(TimeOfDay t) {
    final hour = t.hourOfPeriod == 0 ? 12 : t.hourOfPeriod;
    final minute = t.minute.toString().padLeft(2, '0');
    final period = t.period == DayPeriod.am ? 'AM' : 'PM';
    return '$hour:$minute $period';
  }

  Future<void> _pick(BuildContext context) async {
    final picked = await showTimePicker(
      context: context,
      initialTime: selectedTime ?? TimeOfDay.now(),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: Theme.of(context).colorScheme.copyWith(
                  primary: AppColors.accent,
                ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) onTimeSelected(picked);
  }

  @override
  Widget build(BuildContext context) {
    final displayText =
        selectedTime != null ? _format(selectedTime!) : null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: AppTextStyles.labelLarge),
        const SizedBox(height: AppSpacing.xs),
        GestureDetector(
          onTap: () => _pick(context),
          child: AbsorbPointer(
            child: TextFormField(
              readOnly: true,
              style: AppTextStyles.bodyLarge,
              decoration: InputDecoration(
                hintText: 'Select time',
                prefixIcon: const Icon(
                  Icons.access_time_outlined,
                  color: AppColors.textTertiary,
                  size: 20,
                ),
                errorText: errorText,
              ),
              controller: TextEditingController(text: displayText ?? ''),
            ),
          ),
        ),
      ],
    );
  }
}
