/**
 * Hiển thị kết quả phân loại assets.
 *
 * Props:
 * - data: object chứa { metadata_summary, categories, ai_suggestions }
 * - projectId: string UUID từ backend
 */
export default function ResultView({ data, projectId }) {
  const { metadata_summary, categories, ai_suggestions } = data

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-800">Kết quả phân loại</h2>
        <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
          ID: {projectId?.slice(0, 8)}...
        </span>
      </div>

      {/* Metadata Summary Card */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{metadata_summary.total_assets}</div>
            <div className="text-sm text-gray-500">Tổng tài sản</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-indigo-600">{metadata_summary.total_categories}</div>
            <div className="text-sm text-gray-500">Danh mục</div>
          </div>
        </div>
        {metadata_summary.insights && (
          <p className="mt-3 text-sm text-gray-600 italic border-t border-blue-200 pt-3">
            💡 {metadata_summary.insights}
          </p>
        )}
      </div>

      {/* AI Suggestions */}
      {ai_suggestions?.length > 0 && (
        <div className="bg-yellow-50 rounded-lg border border-yellow-200 p-4">
          <h3 className="font-medium text-yellow-800 mb-2">📋 Đề xuất cải thiện</h3>
          <ul className="space-y-1">
            {ai_suggestions.map((s, i) => (
              <li key={i} className="text-sm text-yellow-700 flex gap-2">
                <span className="text-yellow-500 font-bold">{i + 1}.</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Categories */}
      <div className="space-y-4">
        <h3 className="font-medium text-gray-700">📂 Danh mục tài sản</h3>
        {categories.map((cat, idx) => (
          <div key={idx} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            {/* Category Header */}
            <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
              <div>
                <span className="font-medium text-gray-800">{cat.category_name}</span>
                <span className="ml-2 text-xs text-gray-400 bg-gray-200 px-1.5 py-0.5 rounded">
                  {cat.slug}
                </span>
              </div>
              <span className="text-xs text-gray-500">{cat.assets?.length || 0} assets</span>
            </div>

            {/* Assets Table */}
            {cat.assets?.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-50 text-gray-500 text-xs uppercase">
                      <th className="text-left px-4 py-2 font-medium">Tên gốc</th>
                      <th className="text-left px-4 py-2 font-medium">Slug</th>
                      <th className="text-left px-4 py-2 font-medium">Mô tả</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {cat.assets.map((asset, i) => (
                      <tr key={i} className="hover:bg-gray-50">
                        <td className="px-4 py-2 text-gray-800">{asset.original_name}</td>
                        <td className="px-4 py-2">
                          <code className="text-xs bg-gray-100 px-1.5 py-0.5 rounded text-gray-600">
                            {asset.slug}
                          </code>
                        </td>
                        <td className="px-4 py-2 text-gray-500 text-xs">
                          {asset.description || '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
