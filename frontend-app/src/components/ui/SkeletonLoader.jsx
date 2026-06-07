/**
 * Khối xám nhấp nháy (skeleton) hiển thị khi đang loading.
 * Mô phỏng cấu trúc: metadata card → 3 category cards → mỗi card có vài dòng.
 */
export default function SkeletonLoader() {
  return (
    <div className="animate-pulse space-y-6 p-4">
      {/* Metadata skeleton */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-3">
        <div className="h-5 bg-gray-200 rounded w-1/3" />
        <div className="h-4 bg-gray-200 rounded w-1/2" />
        <div className="h-4 bg-gray-200 rounded w-2/3" />
      </div>

      {/* Category cards skeleton */}
      {[1, 2, 3].map((i) => (
        <div key={i} className="bg-white rounded-lg border border-gray-200 p-4 space-y-3">
          <div className="h-5 bg-gray-200 rounded w-1/4" />
          <div className="h-3 bg-gray-100 rounded w-full" />
          <div className="h-3 bg-gray-100 rounded w-5/6" />
          <div className="h-3 bg-gray-100 rounded w-3/4" />
        </div>
      ))}
    </div>
  )
}
