query_total_problemset_questions = """
    query problemsetQuestionList($categorySlug: String, $filters: QuestionListFilterInput) {
        problemsetQuestionList: questionList(
            categorySlug: $categorySlug
            filters: $filters
        ) {
            total: totalNum
        }
    }
"""
query_problemset_question_list = """query problemsetQuestionList(
        $categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
    problemsetQuestionList: questionList(
      categorySlug: $categorySlug
      limit: $limit
      skip: $skip
      filters: $filters
    ) {
      total: totalNum
      questions: data {
        acRate
        difficulty
        title
        titleSlug
      }
    }
"""
