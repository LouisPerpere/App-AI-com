const buildThumbUrl = (id) => `${API}/content/${id}/thumb?token=${getAccessToken() || ''}`;
const buildOriginalUrl = (id) => `${API}/content/${id}/file?token=${getAccessToken() || ''}`;