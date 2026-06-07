import axios from 'axios'

// Trong dev: Vite proxy /api → localhost:8000
// Trong prod: Nginx proxy /api → backend.railway.app
// Nếu không set VITE_API_URL, fallback về '' → URL là /api/v1/organize-assets
const API_BASE = import.meta.env.VITE_API_URL || ''
const API_URL = `${API_BASE}/api/v1/organize-assets`

/**
 * Gửi yêu cầu phân loại assets lên backend.
 * @param {string} projectName - Tên dự án
 * @param {string} rawText - Danh sách assets thô
 * @returns {Promise<{project_id: string, status: string, data: object}>}
 */
export async function organizeAssets(projectName, rawText) {
  try {
    const response = await axios.post(API_URL, {
      project_name: projectName,
      raw_text: rawText,
    })
    return response.data
  } catch (error) {
    // Axios trả về lỗi trong error.response.data
    const detail =
      error.response?.data?.detail || error.message || 'Lỗi không xác định'
    throw new Error(detail)
  }
}
