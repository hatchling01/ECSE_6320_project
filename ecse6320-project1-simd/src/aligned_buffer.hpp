#pragma once

#include <cstddef>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <type_traits>
#include <vector>

namespace project {

template <typename T>
class AlignedBuffer final {
    static_assert(std::is_same<T, float>::value || std::is_same<T, double>::value,
                  "AlignedBuffer supports float and double.");

public:
    explicit AlignedBuffer(std::size_t size,
                           std::size_t alignment = 64,
                           std::size_t extra_elements = 0)
        : size_(size), alignment_(alignment), extra_elements_(extra_elements) {
        if (alignment_ < alignof(T) || alignment_ % sizeof(T) != 0 ||
            (alignment_ & (alignment_ - 1)) != 0) {
            throw std::invalid_argument(
                "Alignment must be a power of two and a multiple of sizeof(T).");
        }
        if (size_ > std::numeric_limits<std::size_t>::max() - extra_elements_) {
            throw std::length_error("AlignedBuffer capacity overflow.");
        }

        const std::size_t required = size_ + extra_elements_;
        const std::size_t alignment_slots = alignment_ / sizeof(T);
        if (required > std::numeric_limits<std::size_t>::max() - alignment_slots) {
            throw std::length_error("AlignedBuffer allocation size overflow.");
        }
        storage_.resize(required + alignment_slots, T{});

        const auto address = reinterpret_cast<std::uintptr_t>(storage_.data());
        const std::size_t padding_bytes =
            (alignment_ - static_cast<std::size_t>(address % alignment_)) % alignment_;
        if (padding_bytes % sizeof(T) != 0) {
            throw std::logic_error("Cannot align typed storage to requested alignment.");
        }
        prefix_elements_ = padding_bytes / sizeof(T);
    }

    std::size_t size() const noexcept { return size_; }
    std::size_t alignment() const noexcept { return alignment_; }
    std::size_t extra_elements() const noexcept { return extra_elements_; }

    T* data(std::size_t offset_elements = 0) {
        check_offset(offset_elements);
        return storage_.data() + prefix_elements_ + offset_elements;
    }

    const T* data(std::size_t offset_elements = 0) const {
        check_offset(offset_elements);
        return storage_.data() + prefix_elements_ + offset_elements;
    }

private:
    void check_offset(std::size_t offset_elements) const {
        if (offset_elements > extra_elements_) {
            throw std::out_of_range("AlignedBuffer offset exceeds reserved extra elements.");
        }
    }

    std::size_t size_;
    std::size_t alignment_;
    std::size_t extra_elements_;
    std::size_t prefix_elements_ = 0;
    std::vector<T> storage_;
};

}  // namespace project