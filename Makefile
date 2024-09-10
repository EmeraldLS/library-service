public:
	@python ./public/api.py

admin:
	@python ./admin/api.py

.PHONY:
	public admin