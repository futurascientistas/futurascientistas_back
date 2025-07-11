export function objectToFormData(obj: Record<string, any>): FormData {
  const formData = new FormData();

  Object.entries(obj).forEach(([key, value]) => {
    // Se o valor for um arquivo ou blob
    if (value instanceof File || value instanceof Blob) {
      formData.append(key, value);
    }
    // Se for array, adiciona todos com o mesmo nome (ex: checkboxes ou arquivos múltiplos)
    else if (Array.isArray(value)) {
      value.forEach((item, index) => {
        if (item instanceof File || item instanceof Blob) {
          formData.append(`${key}[${index}]`, item);
        } else {
          formData.append(`${key}[${index}]`, String(item));
        }
      });
    }
    // Campos simples (string, number, boolean)
    else if (value !== undefined && value !== null) {
      formData.append(key, String(value));
    }
  });

  return formData;
}
