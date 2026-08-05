// lib/widgets/input/place_field.dart
import 'package:flutter/material.dart';
import '../../theme/app_theme.dart';

class PlaceField extends StatelessWidget {
  final TextEditingController controller;
  final String? errorText;
  final ValueChanged<String>? onChanged;

  const PlaceField({
    super.key,
    required this.controller,
    this.errorText,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Birth Place', style: AppTextStyles.labelLarge),
        const SizedBox(height: AppSpacing.xs),
        TextFormField(
          controller: controller,
          onChanged: onChanged,
          keyboardType: TextInputType.text,
          textCapitalization: TextCapitalization.words,
          style: AppTextStyles.bodyLarge,
          decoration: InputDecoration(
            hintText: 'e.g. Mumbai, India',
            prefixIcon: const Icon(
              Icons.location_on_outlined,
              color: AppColors.textTertiary,
              size: 20,
            ),
            errorText: errorText,
          ),
        ),
      ],
    );
  }
}
