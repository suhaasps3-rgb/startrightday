// lib/widgets/input/date_field.dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../theme/app_theme.dart';

class DateField extends StatelessWidget {
  final String label;
  final DateTime? selectedDate;
  final DateTime firstDate;
  final DateTime lastDate;
  final String hintText;
  final ValueChanged<DateTime> onDateSelected;
  final String? errorText;

  const DateField({
    super.key,
    required this.label,
    required this.selectedDate,
    required this.firstDate,
    required this.lastDate,
    required this.onDateSelected,
    this.hintText = 'Select date',
    this.errorText,
  });

  Future<void> _pick(BuildContext context) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: selectedDate ?? DateTime.now(),
      firstDate: firstDate,
      lastDate: lastDate,
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
    if (picked != null) onDateSelected(picked);
  }

  @override
  Widget build(BuildContext context) {
    final displayText = selectedDate != null
        ? DateFormat('d MMM yyyy').format(selectedDate!)
        : null;

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
                hintText: hintText,
                prefixIcon: const Icon(
                  Icons.calendar_today_outlined,
                  color: AppColors.textTertiary,
                  size: 18,
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
