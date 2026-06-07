import { useForm } from 'react-hook-form'
import Spinner from './ui/Spinner'

/**
 * Form nhập dữ liệu project.
 *
 * Props:
 * - onSubmit(name, text): callback khi submit
 * - isLoading: boolean, disable form khi đang loading
 * - defaultName: string từ localStorage
 * - defaultText: string từ localStorage
 * - onNameChange, onTextChange: cập nhật localStorage
 */
export default function AssetForm({
  onSubmit,
  isLoading,
  defaultName = '',
  defaultText = '',
  onNameChange,
  onTextChange,
}) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      projectName: defaultName,
      rawText: defaultText,
    },
  })

  const handleFormSubmit = (data) => {
    onSubmit(data.projectName, data.rawText)
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      {/* Project Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Tên dự án <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          {...register('projectName', { required: 'Tên dự án không được để trống' })}
          onChange={(e) => onNameChange?.(e.target.value)}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.projectName ? 'border-red-500 ring-red-500' : 'border-gray-300'
          }`}
          placeholder="VD: Nhà máy Ajinomoto Việt Nam"
          disabled={isLoading}
        />
        {errors.projectName && (
          <p className="text-red-500 text-sm mt-1">{errors.projectName.message}</p>
        )}
      </div>

      {/* Raw Text */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Danh sách tài sản <span className="text-red-500">*</span>
        </label>
        <textarea
          rows={8}
          {...register('rawText', {
            required: 'Danh sách tài sản không được để trống',
            minLength: {
              value: 10,
              message: 'Vui lòng nhập ít nhất 10 ký tự',
            },
          })}
          onChange={(e) => onTextChange?.(e.target.value)}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y ${
            errors.rawText ? 'border-red-500 ring-red-500' : 'border-gray-300'
          }`}
          placeholder="VD: máy bơm ly tâm số 1, van xả áp 01 nằm ở khu vực trạm bơm chính..."
          disabled={isLoading}
        />
        {errors.rawText && (
          <p className="text-red-500 text-sm mt-1">{errors.rawText.message}</p>
        )}
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-blue-600 text-white py-2.5 px-4 rounded-lg hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
      >
        {isLoading && <Spinner />}
        {isLoading ? 'Đang phân tích...' : '🚀 Phân loại tài sản'}
      </button>
    </form>
  )
}
