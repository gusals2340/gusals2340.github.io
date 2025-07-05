// shp_worker.js
// 이 파일은 웹 워커로 실행됩니다.

// shp.js 라이브러리 로드
importScripts('https://unpkg.com/shpjs@latest/dist/shp.js');
// simplify-js 라이브러리 로드 (CDN 경로 수정)
console.log('Loading simplify.js from: ./simplify.js');
importScripts('./simplify.js');

let isCancelled = false;

// GeoJSON FeatureCollection의 모든 도형을 재귀적으로 단순화하는 함수
function simplifyGeoJSON(geojson, tolerance) {
    if (!geojson || !geojson.features) {
        return geojson;
    }

    geojson.features.forEach(feature => {
        if (feature.geometry && feature.geometry.coordinates) {
            if (feature.geometry.type === 'Point') {
                // Point는 단순화할 필요 없음
                return;
            } else if (feature.geometry.type === 'LineString') {
                feature.geometry.coordinates = simplify(feature.geometry.coordinates.map(c => ({x: c[0], y: c[1]})), tolerance, false).map(p => [p.x, p.y]);
            } else if (feature.geometry.type === 'Polygon') {
                feature.geometry.coordinates = feature.geometry.coordinates.map(ring => {
                    return simplify(ring.map(c => ({x: c[0], y: c[1]})), tolerance, false).map(p => [p.x, p.y]);
                });
            } else if (feature.geometry.type === 'MultiLineString') {
                feature.geometry.coordinates = feature.geometry.coordinates.map(line => {
                    return simplify(line.map(c => ({x: c[0], y: c[1]})), tolerance, false).map(p => [p.x, p.y]);
                });
            } else if (feature.geometry.type === 'MultiPolygon') {
                feature.geometry.coordinates = feature.geometry.coordinates.map(polygon => {
                    return polygon.map(ring => {
                        return simplify(ring.map(c => ({x: c[0], y: c[1]})), tolerance, false).map(p => [p.x, p.y]);
                    });
                });
            }
            // GeometryCollection 등 다른 타입은 현재 처리하지 않음
        }
    });
    return geojson;
}

self.onmessage = async function(e) {
    const { type, payload } = e.data;

    if (type === 'start_processing') {
        isCancelled = false;
        const tasks = payload.tasks; // Array of {name, shpBuffer, dbfBuffer, prjBuffer}
        const simplificationTolerance = payload.simplificationTolerance || 0.0001; // 기본 단순화 허용 오차

        for (let i = 0; i < tasks.length; i++) {
            if (isCancelled) {
                console.log('Worker: Processing cancelled.');
                self.postMessage({ type: 'processing_cancelled' });
                return;
            }

            const task = tasks[i];
            const currentTaskIndex = i + 1;
            const totalTasksCount = tasks.length;

            // 메인 스레드에 현재 처리 중인 파일 정보와 진행률을 보냅니다.
            console.log(`Worker: Sending progress_update for ${task.name}, current: ${currentTaskIndex}, total: ${totalTasksCount}`);
            self.postMessage({ type: 'progress_update', current: currentTaskIndex, total: totalTasksCount, name: task.name });

            try {
                let geojson = shp.combine([
                    shp.parseShp(task.shpBuffer, task.prjBuffer),
                    shp.parseDbf(task.dbfBuffer)
                ]);

                // SHP 파일 이름을 GeoJSON 피처의 속성에 추가
                const shpFileName = task.name; // task.name은 확장자 없는 파일 이름
                if (geojson && geojson.features) {
                    geojson.features.forEach(feature => {
                        if (!feature.properties) {
                            feature.properties = {};
                        }
                        feature.properties._shpFileName = shpFileName;
                    });
                }

                // 도형 단순화 적용
                if (simplificationTolerance > 0) { // tolerance 변수명 수정
                    geojson = simplifyGeoJSON(geojson, simplificationTolerance);
                }

                console.log(`Worker: Processed ${task.name}. Sending shp_processed.`);
                self.postMessage({ type: 'shp_processed', geojson, name: task.name });
            } catch (error) {
                console.error(`Worker: Error processing ${task.name}:`, error);
                self.postMessage({ type: 'shp_error', name: task.name, error: error.message });
            }
        }
        console.log('Worker: All tasks complete. Sending processing_complete.');
        self.postMessage({ type: 'processing_complete' });

    } else if (type === 'cancel_processing') {
        console.log('Worker: Received cancel_processing request.');
        isCancelled = true;
    }
};
