import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-create-project-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    TranslateModule
  ],
  templateUrl: './create-project-dialog.component.html',
  styleUrl: './create-project-dialog.component.scss'
})
export class CreateProjectDialogComponent implements OnInit {
  projectForm!: FormGroup;

  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<CreateProjectDialogComponent>);

  ngOnInit(): void {
    this.projectForm = this.fb.group({
      project_name: ['', [Validators.required, Validators.maxLength(100)]],
      tags: ['']
    });
  }

  /**
   * Get form field error message.
   */
  getFieldError(fieldName: string): string {
    const field = this.projectForm.get(fieldName);
    if (!field || !field.errors || !field.touched) {
      return '';
    }

    if (field.errors['required']) {
      return 'songProjects.validation.required';
    }
    if (field.errors['maxLength']) {
      return `songProjects.validation.maxLength`;
    }
    return '';
  }

  /**
   * Submit form and close dialog with data.
   */
  onSubmit(): void {
    if (this.projectForm.invalid) {
      this.projectForm.markAllAsTouched();
      return;
    }

    const formValue = this.projectForm.value;

    // Convert comma-separated tags to array
    const tags = formValue.tags
      ? formValue.tags.split(',').map((tag: string) => tag.trim()).filter((tag: string) => tag.length > 0)
      : [];

    this.dialogRef.close({
      project_name: formValue.project_name.trim(),
      tags: tags
    });
  }

  /**
   * Close dialog without saving.
   */
  onCancel(): void {
    this.dialogRef.close();
  }
}
