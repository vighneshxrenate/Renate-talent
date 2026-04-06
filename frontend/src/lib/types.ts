export interface College {
  id: string;
  name: string;
  slug: string;
}

export interface Industry {
  id: string;
  name: string;
  slug: string;
}

export interface SubmissionResponse {
  id: string;
  message: string;
}

export interface ApiError {
  detail: string;
}
