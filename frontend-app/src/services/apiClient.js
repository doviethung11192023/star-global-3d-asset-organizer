import axios from 'axios'

const API_URL = '/api/v1/organize-assets'

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
