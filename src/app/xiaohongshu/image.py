class Image:
    def __init__(self, image_list, type):
        self.image_list = image_list
        self.type = type

    # 获取图片token
    @staticmethod
    def get_image_token(url):
        arr = url.split("/")
        if "notes_pre_post" in arr:
            return "/notes_pre_post/" + arr[-1].split("!")[0]
        else:
            return arr[-1].split("!")[0]

    # 生成webp链接
    @staticmethod
    def __generate_webp_link(token: str) -> str:
        return f"https://sns-img-bd.xhscdn.com/{token}"

    # 生成png链接
    @staticmethod
    def __generate_png_link(token: str) -> str:
        return f"https://ci.xiaohongshu.com/{token}?imageView2/format/png"

    def to_dict(self):
        if self.type == "webp":
            for image in self.image_list:
                token = self.get_image_token(image)
                yield self.__generate_webp_link(token)
        elif self.type == "png":
            for image in self.image_list:
                token = self.get_image_token(image)
                yield self.__generate_png_link(token)
        else:
            return self.image_list
