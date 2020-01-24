from ariadne import gql

type_defs = gql("""
    input CreateUserInput {
        name: String!
        email: String!
        password: String!
    }
    input UpdateUserInput {
        email: String
        name: String
        night_mode: Boolean
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
    type User {
        id: ID!
        email: String!
        name: String!
        night_mode: Boolean!
        posts: [Post]
    }
    type Post {
        id: ID!
        title: String!
        text: String!
        user: User!
        published: Boolean!
        createdAt: Float!
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
        users(emails: [String] user_ids: [String]): [User]!
        post(post_id: ID user_id:ID): [Post]
        comment(comment_id: ID): Comment
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
    }
    type Subscription{
        count: Int
    }
""")
