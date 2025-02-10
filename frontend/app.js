const API_BASE_URL = 'http://127.0.0.1:8000';

new Vue({
    el: '#app',
    data: {
        paintings: [],
        currentPainting: {
            title: '',
            artist: '',
            dynasty: '',
            category: '',
            description: '',
            painting_metadata: ''
        },
        dynastyStats: [],
        categoryStats: [],
        editMode: false,
        editId: null,
        selectedImage: null,
        selectedJson: null
    },
    methods: {
        // 获取所有画作
        fetchPaintings() {
            axios.get(`${API_BASE_URL}/api/paintings/`)
                .then(response => {
                    this.paintings = response.data;
                })
                .catch(error => {
                    console.error('获取画作列表失败:', error);
                    alert('获取画作列表失败');
                });
        },

        // 获取统计数据
        fetchStats() {
            // 获取朝代统计
            axios.get(`${API_BASE_URL}/api/analytics/dynasty`)
                .then(response => {
                    this.dynastyStats = response.data;
                })
                .catch(error => {
                    console.error('获取朝代统计失败:', error);
                });

            // 获取类别统计
            axios.get(`${API_BASE_URL}/api/analytics/category`)
                .then(response => {
                    this.categoryStats = response.data;
                })
                .catch(error => {
                    console.error('获取类别统计失败:', error);
                });
        },

        // 保存画作（创建或更新）
        savePainting() {
            // 处理painting_metadata
            let paintingData = {...this.currentPainting};
            if (typeof paintingData.painting_metadata === 'string') {
                try {
                    paintingData.painting_metadata = paintingData.painting_metadata ? JSON.parse(paintingData.painting_metadata) : null;
                } catch (e) {
                    alert('元数据JSON格式无效');
                    return;
                }
            }

            const method = this.editMode ? 'put' : 'post';
            const url = this.editMode 
                ? `${API_BASE_URL}/api/paintings/${this.editId}`
                : `${API_BASE_URL}/api/paintings/`;

            axios[method](url, paintingData)
                .then(response => {
                    this.fetchPaintings();
                    this.fetchStats();
                    this.resetForm();
                    alert(this.editMode ? '更新成功' : '添加成功');
                })
                .catch(error => {
                    console.error('保存失败:', error);
                    alert('保存失败');
                });
        },

        // 编辑画作
        editPainting(painting) {
            this.editMode = true;
            this.editId = painting.id;
            this.currentPainting = {
                ...painting,
                painting_metadata: painting.painting_metadata ? JSON.stringify(painting.painting_metadata, null, 2) : ''
            };
        },

        // 删除画作
        deletePainting(id) {
            if (confirm('确定要删除这个画作吗？')) {
                axios.delete(`${API_BASE_URL}/api/paintings/${id}`)
                    .then(response => {
                        this.fetchPaintings();
                        this.fetchStats();
                        alert('删除成功');
                    })
                    .catch(error => {
                        console.error('删除失败:', error);
                        alert('删除失败');
                    });
            }
        },

        // 处理图片文件选择
        handleImageChange(event) {
            this.selectedImage = event.target.files[0];
        },

        // 处理JSON文件选择
        handleJsonChange(event) {
            this.selectedJson = event.target.files[0];
        },

        // 上传文件
        async uploadFiles() {
            if (!this.selectedImage || !this.selectedJson) {
                alert('请同时选择图片文件和对应的JSON文件');
                return;
            }

            // 检查文件名是否匹配（除了扩展名外应该相同）
            const imgName = this.selectedImage.name.replace(/\.[^/.]+$/, "");
            const jsonName = this.selectedJson.name.replace(/\.[^/.]+$/, "");
            
            if (imgName !== jsonName) {
                alert('请确保图片文件和JSON文件的文件名相同（除扩展名外）');
                return;
            }

            const formData = new FormData();
            formData.append('image', this.selectedImage);
            formData.append('json_file', this.selectedJson);

            try {
                const response = await axios.post(
                    `${API_BASE_URL}/api/upload-pair`,
                    formData,
                    {
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        }
                    }
                );
                alert('文件对上传成功');
                this.fetchPaintings();
                this.selectedImage = null;
                this.selectedJson = null;
            } catch (error) {
                console.error('文件上传失败:', error);
                alert('文件上传失败: ' + (error.response?.data?.detail || error.message));
            }
        },

        // 重置表单
        resetForm() {
            this.currentPainting = {
                title: '',
                artist: '',
                dynasty: '',
                category: '',
                description: '',
                painting_metadata: ''
            };
            this.editMode = false;
            this.editId = null;
            this.selectedImage = null;
            this.selectedJson = null;
        }
    },
    mounted() {
        // 页面加载时获取数据
        this.fetchPaintings();
        this.fetchStats();
    }
}); 