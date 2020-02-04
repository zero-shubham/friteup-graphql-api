from ariadne import gql

type_defs = gql("""
    enum VoteTypes {
        UP_VOTE
        DOWN_VOTE
    }
    input CreateUserInput {
        name: String!
        email: String!
        password: String!
    }
    input UpdateUserInput {
        email: String
        name: String
        night_mode: Boolean
        bio: String
    }
    input UpdatePostInput {
        post_id: ID!
        text: String
        title: String
        published: Boolean
    }
    type Login {
        user: User!
    }
    type Validate {
        user_id: ID!
        valid: Boolean!
    }
    type Logout {
        logged_out: Boolean!
    }
    type Response {
        message: String!
    }
    type Search {
        users: [User]
        posts: [Post]
    }
    type User {
        id: ID!
        email: String!
        name: String!
        bio: String!
        night_mode: Boolean!
        subscribers: [String]
        subscribed: [String]
        posts: [Post]
    }
    type Post {
        id: ID!
        title: String!
        text: String!
        user_id: String!
        user: User
        published: Boolean!
        created_at: Float!
        up_vote: [String]
        down_vote: [String]
        comments: [Comment]
    }
    type Comment {
        id: ID!
        text: String!
        post: Post!
        user: User!
    }
    type Query {
        user_validate(user_id: ID): Validate
        user(email: String user_id: ID): User
        users(emails: [String] user_ids: [ID]): [User]!
        post(post_id: ID user_id:ID): [Post]
        comment(comment_id: ID): Comment
        search(keyword: String!): Search
        feed: [Post]
    }
    type Mutation {
        create_user(data: CreateUserInput!): User
        create_post(text: String! title: String! published: Boolean!): Post
        create_comment(post_id: ID! text: String!): Comment
        update_user(data: UpdateUserInput!): User
        update_post(data: UpdatePostInput!): Post
        update_comment(comment_id: ID! text: String!): Comment
        delete_user(email: String!): User
        delete_comment(comment_id: ID!): Comment
        delete_post(post_id:  ID!): Post
        login(email: String! password: String!): Login
        logout: Logout
        change_password(old_password: String! new_password: String!): Boolean!
        subscribe_user(user_id: ID!): Boolean!
        unsubscribe_user(user_id: ID!): Boolean!
        vote_post(post_id: ID! vote_type: VoteTypes!): Post
    }
    type Subscription{
        count: Int
    }
""")
