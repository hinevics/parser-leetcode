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
        $categorySlug: String, $limit: Int, $filters: QuestionListFilterInput) {
    problemsetQuestionList: questionList(
      categorySlug: $categorySlug
      limit: $limit
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
}
"""

query_get_total_num_sols = """
  query communitySolutions(
    $questionSlug: String!,
    $skip: Int!,
    $first: Int!,
    $query: String,
    $orderBy: TopicSortingOption,
    $languageTags: [String!],
    $topicTags: [String!]
  ) {
    questionSolutions(
      filters: {
        questionSlug: $questionSlug,
        skip: $skip,
        first: $first,
        query: $query,
        orderBy: $orderBy,
        languageTags: $languageTags,
        topicTags: $topicTags
      }
    ) {
      totalNum
    }
}
"""
query_algorithm_solutions = """
query communitySolutions(
  $questionSlug: String!,
  $skip: Int!,
  $first: Int!,
  $query: String,
  $orderBy: TopicSortingOption,
  $languageTags: [String!],
  $topicTags: [String!]
) {
  questionSolutions(
    filters: {
      questionSlug: $questionSlug,
      skip: $skip,
      first: $first,
      query: $query,
      orderBy: $orderBy,
      languageTags: $languageTags,
      topicTags: $topicTags
    }
  ) {
    totalNum
    solutions {
      id
      title
      commentCount
      topLevelCommentCount
      viewCount
      solutionTags {
        name
        slug
      }
      post {
        id
        content
        status
        voteCount
        creationDate
        author {
          username
            profile {
                reputation
            }
        }
      }
    }
  }
}
"""

query_question_сontent = """
    query questionContent($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            content
            mysqlSchemas
        }
    }
"""
