import { useState } from 'react'
import toast from 'react-hot-toast'
import AssetForm from './components/AssetForm'
import ResultView from './components/ResultView'
import SkeletonLoader from './components/ui/SkeletonLoader'
import { organizeAssets } from './services/apiClient'
import { useAutoSave } from './hooks/useAutoSave'

function App() {
  // States
  const [result, setResult] = useState(null) // { project_id, status, data }
  const [isLoading, setIsLoading] = useState(false)

  // Auto-save hook (localStorage)
  const { projectName, setProjectName, rawText, setRawText } = useAutoSave()

  /**
   * Xử lý submit form.
   * - Gọi API
   * - Nếu lỗi → hiển thị toast
   * - Nếu thành công → set result
   */
  const handleSubmit = async (name, text) => {
    setIsLoading(true)
    setResult(null)

    try {
      const data = await organizeAssets(name, text)
      setResult(data)
      toast.success('✅ Phân loại tài sản thành công!')
    } catch (error) {
      toast.error(`❌ ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="text-xl font-bold text-gray-800">
            🏗️ AI 3D Asset Organizer
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Phân loại tài sản 3D tự động bằng Gemini AI
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Form */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              📝 Nhập dữ liệu
            </h2>
            <AssetForm
              onSubmit={handleSubmit}
              isLoading={isLoading}
              defaultName={projectName}
              defaultText={rawText}
              onNameChange={setProjectName}
              onTextChange={setRawText}
            />
          </div>

          {/* Right Column: Result / Skeleton / Empty */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              📊 Kết quả
            </h2>

            {isLoading ? (
              <SkeletonLoader />
            ) : result ? (
              <ResultView data={result.data} projectId={result.project_id} />
            ) : (
              /* Empty state: hướng dẫn */
              <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                <div className="text-6xl mb-4">📋</div>
                <p className="text-sm">Nhập dự án và danh sách tài sản ở cột bên trái</p>
                <p className="text-xs mt-1">Sau đó bấm "Phân loại tài sản"</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
