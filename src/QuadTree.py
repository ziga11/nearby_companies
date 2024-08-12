class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, coords):
        return (
            self.x - self.width / 2 <= coords.x <= self.x + self.width / 2
            and self.y - self.height / 2 <= coords.y <= self.y + self.height / 2
        )

    def intersects(self, range_rect):
        return not (
            range_rect.x - range_rect.width / 2 > self.x + self.width / 2
            or range_rect.x + range_rect.width / 2 < self.x - self.width / 2
            or range_rect.y - range_rect.height / 2 > self.y + self.height / 2
            or range_rect.y + range_rect.height / 2 < self.y - self.height / 2
        )


class QuadTree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary
        self.capacity = capacity
        self.children = []
        self.divided = False

    def subdivide(self):
        x = self.boundary.x
        y = self.boundary.y
        w = self.boundary.width / 2
        h = self.boundary.height / 2

        nw_boundary = Rectangle(x - w / 2, y - h / 2, w, h)
        ne_boundary = Rectangle(x + w / 2, y - h / 2, w, h)
        sw_boundary = Rectangle(x - w / 2, y + h / 2, w, h)
        se_boundary = Rectangle(x + w / 2, y + h / 2, w, h)

        self.nw = QuadTree(nw_boundary, self.capacity)
        self.ne = QuadTree(ne_boundary, self.capacity)
        self.sw = QuadTree(sw_boundary, self.capacity)
        self.se = QuadTree(se_boundary, self.capacity)
        self.divided = True

    def insert(self, child):
        if not self.boundary.contains(child):
            return False

        if len(self.children) < self.capacity:
            self.children.append(child)
            return True

        if not self.divided:
            self.subdivide()

        if (
            self.nw.insert(child)
            or self.ne.insert(child)
            or self.sw.insert(child)
            or self.se.insert(child)
        ):
            return True

        return False

    def query(self, range_rect, found):
        if not self.boundary.intersects(range_rect):
            return

        for job in self.children:
            if range_rect.contains(job):
                found.append(job)

        if self.divided:
            self.nw.query(range_rect, found)
            self.ne.query(range_rect, found)
            self.sw.query(range_rect, found)
            self.se.query(range_rect, found)
