import { z } from "zod";

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

export const submissionSchema = z.object({
  student_name: z
    .string()
    .min(1, "Full name is required")
    .max(200, "Name is too long"),
  email: z.string().email("Enter a valid email address"),
  phone: z
    .string()
    .regex(/^\d{10}$/, "Enter a valid 10-digit mobile number"),
  college_id: z.string().min(1, "Please select a college"),
  industry_id: z.string().min(1, "Please select an industry"),
  note: z.string().max(1000, "Note is too long").optional().or(z.literal("")),
  resume: z
    .custom<FileList>()
    .refine((files) => files && files.length > 0, "Resume is required")
    .refine(
      (files) => files && files[0]?.type === "application/pdf",
      "Only PDF files are accepted"
    )
    .refine(
      (files) => files && files[0]?.size <= MAX_FILE_SIZE,
      "File size must be under 5MB"
    ),
});

export type SubmissionFormData = z.infer<typeof submissionSchema>;
